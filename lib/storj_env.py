import json
from datetime import datetime
from ext import python_libstorj as pystorj


class StorjEnv():
    def __init__(self,
                 bridge_options,
                 encrypt_options,
                 http_options,
                 log_options):

        options_list = (
            (bridge_options, pystorj.BridgeOptions()),
            (encrypt_options, pystorj.EncryptOptions()),
            (http_options, pystorj.HttpOptions()),
            (log_options, pystorj.LogOptions())
        )

        for option_pair in options_list:
            (options, option_struct) = option_pair
            for key, value in options.viewitems():
                if key == 'pass':
                    # NB: `pass` is a reserved attribute name; swig
                    #     knows this and has changed `pass` to `_pass`
                    key = '_pass'
                setattr(option_struct, key, value)

        options = zip(*options_list)[1]
        self.env = pystorj.init_env(*options)
        self.env.loop = pystorj.set_loop(self.env)

    def destroy(self):
        pystorj.destroy_env(self.env)

    def get_info(self, handle):
        def handle_(error, result):
            result_object = json.loads(result)
            handle(error, result_object)
        pystorj.get_info(self.env, handle_)
        pystorj.run(self.env.loop)

    def list_buckets(self, callback=None):
        results = []

        def handle_(error, buckets):
            for i, bucket in enumerate(buckets):
                iso8601_format = '%Y-%m-%dT%H:%M:%S.%fZ'
                created_date = datetime.strptime(bucket['created'], iso8601_format)
                buckets[i]['created'] = created_date
            results.append(error)
            results.append(buckets)

            if callback:
                return callback(*results)

            if error:
                raise Exception(error)

        pystorj.list_buckets(self.env, handle_)
        pystorj.run(self.env.loop)
        return results[1]

    def create_bucket(self, name, callback=None):
        results = []

        def handle_(error, bucket):
            results.append(error)
            results.append(bucket)

            if callback:
                return callback(*results)

            if error:
                raise Exception(error)

        pystorj.create_bucket(self.env, name, handle_)
        pystorj.run(self.env.loop)
        return results[1]

    def delete_bucket(self, bucket_id, callback=None):
        results = []

        def handle_(error):
            results.append(error)

            if callback:
                return callback(*results)

            if error:
                raise Exception(error)

        pystorj.delete_bucket(self.env, bucket_id, handle_)
        pystorj.run(self.env.loop)

    def list_files(self, bucket_id, callback=None):
        results = []

        def handle_(error, files):
            for i, file_ in enumerate(files):
                iso8601_format = '%Y-%m-%dT%H:%M:%S.%fZ'
                created_date = datetime.strptime(file_['created'], iso8601_format)
                files[i]['created'] = created_date
            results.append(error)
            results.append(files)

            if callback:
                return callback(*results)

            if error:
                raise Exception(error)

        pystorj.list_files(self.env, bucket_id, handle_)
        pystorj.run(self.env.loop)
        return results[1]
