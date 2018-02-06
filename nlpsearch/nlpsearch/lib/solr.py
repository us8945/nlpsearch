'''
Created on Nov 5, 2017

@author: Uri Smashnov
'''
import pysolr
import subprocess
import urllib.request as urlq
import json

DEFAULT_PORT = 8983

FIELD_PROPERTIES = [
    'name',
    'type',
    'default',
    'indexed',
    'stored',
    'docValues',
    'sortMissingFirst',
    'sortMissingLast',
    'multiValued',
    'omitNorms',
    'omitTermFreqAndPositions',
    'omitPositions',
    'termVectors',
    'termPositions',
    'termOffsets',
    'termPayloads',
    'required',
    'useDocValuesAsStored',
    'large']

FIELD_TYPE_PROPERTIES = FIELD_PROPERTIES[:] + [
    'name',
    'class',
    'positionIncrementGap',
    'autoGeneratePhraseQueries',
    'enableGraphQueries',
    'docValuesFormat',
    'postingsFormat']


class Solr(object):
    def __init__(self, solr=None, port=DEFAULT_PORT, verbose=False):
        ''' Initialize default settings.
        Args:
            solr: path to solr executable; if not provided, assumes Solr's bin
                is on PATH
            port: to which to connect.
        '''
        self.solr_bin = solr if solr else 'solr'
        self.port = port
        self.pysolr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
        self.core = None
        self.verbose = verbose

    def _run_solr_cmd(self, *args, verbose=False):
        cmd = [self.solr_bin,
               ]
        cmd += args
        if verbose or self.verbose:
            print('Run Solr cmd:',cmd)

        run = subprocess.run(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, check=False)
        if verbose or self.verbose:
            print('After executing command:',cmd)
        return run.returncode, run.stdout, run.stderr

    def start(self, verbose=False):
        return self._run_solr_cmd('start', verbose=verbose)

    def restart(self, port=None, verbose=False):
        if not port:
            port = self.port
        #return self._run_solr_cmd('restart', '-p', str(port), verbose=verbose)
        return self._run_solr_cmd('restart -p {}'.format(port), verbose=verbose)

    def stop(self, verbose=False):
        return self._run_solr_cmd('stop', verbose=verbose)

    def create_core(self, name, confdir='', port=None, verbose=False):
        ''' Adds core named name to Solr instance.

        Args:
            name: name of the core to add
            configdir: to copy and use
            port: overrides instance port number
            verbose: prints activity

        Returns:
            tuple of (returncode, stdout, stderr)
        '''
        verbose = verbose or self.verbose
        if not port:
            port = self.port

        # for thos command report "missing required argument name"
        '''
        url = 'http://localhost:{p}/solr/admin/cores?action=CREATE&'\
        'name={n}&instanceDir={n}&config={c}solrconfig.xml&'\
        'dataDir=data'.format(p=port, n=name, c=confdir)
        if verbose:
            print(url)
        req = urlq.Request(url)
        result = self._get_url_response(req)
        return result
        '''

        cmd = ["create_core", "-c", name]

        if confdir:
            cmd += ["-d", confdir]

        if not port:
            port = self.port
        cmd += ["-p",  str(port)]

        if verbose:
            cmd += ["-V"]

        returncode, stdout, stderr = self._run_solr_cmd(*cmd, verbose=verbose)
        # more settings if successful
        if returncode == 0:
            self._unset_default(name, port)

        self.core = name

        return returncode, stdout, stderr

    def set_core(self, name):
        self.core = name

    def status_core(self, name, port=None, verbose=False):
        if not port:
            port = self.port

        url = 'http://localhost:{p}/solr/admin/cores?action=STATUS&core={c}'.format(p=port, c=name)
        if verbose or self.verbose:
            print(url)
        req = urlq.Request(url)
        result = self._get_url_response(req)
        return json.loads(result)

    def is_core(self, name, port=None, verbose=False):
        status_raw = self.status_core(name, port=port, verbose=verbose)
        status = status_raw['status'][name]
        return len(status) > 0

    def delete_core(self, name, deleteConfig=True, port=None, verbose=False):
        '''solr delete -c
        '''

        if not port:
            port = self.port

        deleteConfig = str(deleteConfig).lower()
        url = 'http://localhost:{p}/solr/admin/cores?action=UNLOAD&'\
              'core={n}&deleteIndex={d}&deleteDataDir={d}&'\
              'deleteInstanceDir={d}'\
              .format(p=port, n=name, d=deleteConfig)
        if verbose or self.verbose:
            print(url)
        req = urlq.Request(url)
        result = self._get_url_response(req)
        return result

    def _make_request_data(self, cmd, **kwargs):
        data = {cmd: kwargs}
        return data

    def _validate_field_definition_properties(self, **kwargs):
        unknown = (set(kwargs.keys()) - set(FIELD_PROPERTIES))

        if len(unknown) > 0:
            raise RuntimeError("Unknown field properties: {}".format(unknown))

    def _validate_field_type_definition_properties(self, **kwargs):
        unknown = (set(kwargs.keys()) - set(FIELD_TYPE_PROPERTIES))

        if len(unknown) > 0:
            raise RuntimeError("Unknown field properties: {}".format(unknown))

    def add_field(self, core=None, port=None, verbose=False, **properties):
        ''' Adds field to schema.
        Args:
            properties:
                https://lucene.apache.org/solr/guide/7_0/defining-fields.html#defining-fields
        '''
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        self._validate_field_definition_properties(**properties)

        data = self._make_request_data("add-field", **properties)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def replace_field(self, core=None, port=None, verbose=False, **properties):
        ''' Replaces field with new properties.

        Args:
            properties: 
                https://lucene.apache.org/solr/guide/7_0/defining-fields.html#defining-fields
        '''
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        self._validate_field_definition_properties(**properties)

        data = self._make_request_data("replace-field", **properties)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def delete_field(self, name, core=None, port=None, verbose=False):
        core = core if core is not None else self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        if port is None:
            port = self.port
        data = {"delete-field": {"name": name}}
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def add_dynamic_field(self, core=None, port=None, verbose=False, **properties):
        ''' Add dynamic field.

        Args:
            properties:
                https://lucene.apache.org/solr/guide/7_0/defining-fields.html#defining-fields
        '''
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        self._validate_field_definition_properties(**properties)

        data = self._make_request_data("add-dynamic-field", **properties)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def delete_dynamic_field(self, name, core=None, port=None, verbose=False):
        core = core if core is not None else self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!."

        if port is None:
            port = self.port
        data = {"delete-dynamic-field": {"name": name}}
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def replace_dynamic_field(self, core=None, port=None, verbose=False, **properties):
        ''' Replaces dynamic field

        Args:
            properties:
                https://lucene.apache.org/solr/guide/7_0/defining-fields.html#defining-fields
        '''
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        self._validate_field_definition_properties(**properties)

        data = self._make_request_data("replace-dynamic-field", **properties)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def add_field_type(self, core=None, port=None, verbose=False, **properties):
        ''' Adds field to schema.

        Args:
            properties: 
                https://lucene.apache.org/solr/guide/7_0/field-type-definitions-and-properties.html#field-type-definitions-and-properties
        '''
        if core is None:
            core = self.core
        assert (core is not None), "Core must be provided or set prior to to call!"

        self._validate_field_type_definition_properties(**properties)

        data = self._make_request_data("add-field-type", **properties)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def delete_field_type(self, name, core=None, port=None, verbose=False):
        core = core if core is not None else self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        if port is None:
            port = self.port
        data = {"delete-field-type": {"name": name}}
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def replace_field_type(self, core=None, port=None, verbose=False, **properties):
        ''' replaces field to schema.

        Args:
            properties: 
                https://lucene.apache.org/solr/guide/7_0/field-type-definitions-and-properties.html#field-type-definitions-and-properties
        '''
        if core is None:
            core = self.core
        assert (core is not None), "Core must be provided or set prior to to call!"

        self._validate_field_type_definition_properties(**properties)

        data = self._make_request_data("replace-field-type", **properties)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def add_copy_field(self, core=None, port=None, verbose=False, source=None, *destinations):
        ''' add copy source field to targets
        '''
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        data = self._make_request_data("add-copy-field", source=source, dest=destinations)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def delete_copy_field(self, core=None, port=None, verbose=False, source=None, dest=None):
        ''' add copy source field to targets
        '''
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        data = self._make_request_data("delete-copy-field", source=source, dest=dest)
        jdata = json.dumps(data).encode()

        return self._post_schema(jdata, core=core, port=port, verbose=verbose)

    def _post_schema(self, data, core=None, port=None, verbose=False):
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"
        if port is None:
            port = self.port

        url = self._get_url("schema", core, port)

        return self._post(url, data, verbose=verbose)

    def _post_config(self, data, core=None, port=None, verbose=False):
        if core is None:
            core = self.core
        assert (core is not None), \
            "Core must be provided or set prior to to call!"

        if port is None:
            port = self.port
        url = self._get_url("config", core, port)

        return self._post(url, data, verbose=verbose)

    def _post(self, url, data, verbose=False):
        if self.verbose or verbose:
            print(url, data)
        req = urlq.Request(url, data, {'Content-Type': 'application/json'})
        result = self._get_url_response(req)
        return result

    def _get_url(self, target, core, port):
        if target == 'schema':
            url = 'http://localhost:{}/solr/{}/schema'.format(port, core)
        elif target == 'config':
            url = 'http://localhost:{}/solr/{}/config'.format(port, core)
        else:
            raise RuntimeError("Unknown target: {}".format(target))

        return url

    def _get_url_response(self, req):
        result = b""
        f = urlq.urlopen(req)
        for x in f:
            result += x
        f.close()
        return result.decode()

    def _unset_default(self, core=None, port=None):
        data = {"set-user-property": {"update.autoCreateFields": False}}
        jdata = json.dumps(data).encode()

        return self._post_config(jdata, core=core, port=port)


if __name__ == '__main__':
    s = Solr(solr='/apps/solr/solr-7.1.0/bin/solr', verbose=True)

    r = s.restart()
    r = s.create_core(name='nlp',)
    print('create:', r)
    s.set_core('nlp')
    r = s.add_field(name="myid1", type="pdate")
    print('add field:', r)
    r = s.add_field(name="myid2", type="pdate")
    print('add field:', r)
    r = s.delete_field("myid1")
    print('delete field:', r)
    # r = s.delete_core('nlp')
    # print('delete:', r)

    r = s.start()
    r = s.create_core('mycore',)
    r = s.add_field(name="word", type="string", indexed=True, stored=False, multiValued=True)
    r = s.add_field(name="sentence", type="string", indexed=False, stored=True, multiValued=True)
    r = s.add_field(name="title", type="string", indexed=False, stored=True, multiValued=True)
    r = s.add_field(name="file", type="string", indexed=False, stored=True, multiValued=True)
