from guesttemplates import blank_template
import httplib
import json
import os
import tarfile
import StringIO
import time
import urllib
import os.path

# List of places to look for config files. The paths are ordered by
# ascending priority.

def log(msg):
    """Log msg to stdout."""

    print msg

class Loader(object):
    """Manages loading guest templates from disk into XAPI."""

    def __init__(self, session):
        self._session = session
        self._confs = {}
        self._by_uuid = {}
        self._by_reflabel = {}

        pools = session.xenapi.pool.get_all_records()
        pool = [i for i in pools][0]
        master = session.xenapi.pool.get_master(pool)
        record = session.xenapi.host.get_record(master)
        version = record['software_version']['xapi']
        self._xapi_version = version.split('.')

    def find_config_files(self, *args):
        """Create a dictionary of the template configs on the filesystem."""

        for path in args:
            self._confs.update((i, os.path.join(path, i)) for i in os.listdir(path) if i.endswith('.json'))

    def _load_template(self, fname):
        """Read JSON template and create a template object. If one template
        derives from another load that and apply changes upon that."""

        with open(fname) as templatefile:
            template = json.load(templatefile)

        if 'derived_from' in template:
            # load base template and overlay deltas
            ret = self._load_template(self._confs[template['derived_from']])
            ret.update(template)
        else:
            ret = blank_template.BaseTemplate(template)

        return ret

    def load_templates(self):
        """Load all known templates from disk."""

        for fname in self._confs.itervalues():
            log("Load %s" % fname)
            template = self._load_template(fname)
            if hasattr(template, 'uuid'):
                self._by_uuid[template.uuid] = template
                self._by_reflabel[template.reference_label] = template

    def _destroy_template(self, ref, record):
        """Destroy a template in XAPI."""

        log("Destroy %s" % record['uuid'])
        self._session.xenapi.VM.set_is_a_template(ref, False)
        record['other_config']['default_template'] = 'false'
        self._session.xenapi.VM.set_other_config(ref, record['other_config'])
        self._session.xenapi.VM.destroy(ref)

    def remove_old_templates(self):
        """Remove outdated templates in XAPI."""

        query = 'field "is_a_template" = "true" and field "is_a_snapshot" = "false"'
        templates = self._session.xenapi.VM.get_all_records_where(query)
        for ref in templates:
            record = templates[ref]
            uuid = record['uuid']
            reflabel = record.get('reference_label', None)

            if (record['other_config'].has_key('default_template') and
                    record['other_config']['default_template'] == 'true'):
                if (uuid in self._by_uuid and
                        record['user_version'] != str(self._by_uuid[uuid].user_version)):
                    self._destroy_template(ref, record)
                    continue

                if (reflabel and reflabel in self._by_reflabel and
                        uuid != self._by_reflabel[reflabel].uuid):
                    self._destroy_template(ref, record)
                    continue

            if uuid in self._by_uuid:
                del self._by_uuid[uuid]

    @staticmethod
    def _make_tar(name, data):
        """Return a tar-formatted string containing 'data' in a file
        called 'name'."""

        datafh = StringIO.StringIO(data)
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(data)
        tarinfo.mtime = time.time()

        tarfh = StringIO.StringIO()
        tar = tarfile.TarFile(fileobj=tarfh, mode='w')
        tar.addfile(tarinfo, fileobj=datafh)
        tar.close()
        datafh.close()

        tarfh.seek(0)
        out = tarfh.read()
        tarfh.close()

        return out

    def _insert_template(self, template):
        """Insert a template into XAPI."""

        log("Insert %s" % template.uuid)

        # Generate ova.xml
        version = {'hostname': 'localhost',
                   'date': '1970-01-01',
                   'product_version': '0.0',
                   'product_brand': 'product',
                   'build_number': '0x',
                   'xapi_major': self._xapi_version[0],
                   'xapi_minor': self._xapi_version[1],
                   'export_vsn': '2'}
        tar = self._make_tar('ova.xml', template.toxml(version))

        # Import XS template.
        task_ref = self._session.xenapi.task.create("import-%s" % template.uuid, "Import of template %s" % template.uuid)
        conn = httplib.HTTPConnection("localhost", 80)
        params = urllib.urlencode({'session_id': self._session._session, 'task_id': task_ref, 'restore': 'true', 'uuid': template.uuid})
        conn.request("PUT", "/import_metadata?" + params, tar)
        conn.getresponse()

        # Wait for import to complete.
        task_status = 'pending'
        count = 0
        while task_status == 'pending' and count < 20:
            count += 1
            time.sleep(0.5)
            task_status = self._session.xenapi.task.get_status(task_ref)
        self._session.xenapi.task.destroy(task_ref)
        if task_status == 'pending':
            raise RuntimeError("Template import timeout")

        # Set default_template = true
        template_ref = self._session.xenapi.VM.get_by_uuid(template.uuid)
        other_config = self._session.xenapi.VM.get_other_config(template_ref)
        other_config['default_template'] = 'true'
        self._session.xenapi.VM.set_other_config(template_ref, other_config)

    def insert_templates(self):
        """Insert all known top-level templates into XAPI."""

        for i in self._by_uuid.itervalues():
            self._insert_template(i)
