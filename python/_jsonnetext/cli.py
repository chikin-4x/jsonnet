import click
import _jsonnet
import json
import pathlib

def get_file_contents(filepath):
    with open(filepath, 'r') as infile:
        return infile.read()

def get_native_dict(native_contents):
    if not native_contents:
        return None
    code = compile(native_contents, "jsonnet_functions.py", 'exec')
    global_vars = {}
    local_vars = {}
    exec(code, global_vars, local_vars)
    native_callbacks = local_vars.get('native_callbacks')
    return native_callbacks

def render_jsonnet(jsonnet_path=None, functions_path=None, tla_str=None, ext_var=None):
    account_alias = 'fakealias'
    env = 'prod'
    if jsonnet_path:
        jsonnet_path = pathlib.Path(jsonnet_path)
    else:
        jsonnet_path = pathlib.Path('./manifest.jsonnet')
    if functions_path:
        jsonnet_functions_path = pathlib.Path(functions_path)
    else:
        jsonnet_functions_path = jsonnet_path.parent / 'jsonnet_functions.py'
    func_dict = None
    ext_vars = {}
    if ext_vars == {}:
        ext_vars = {
            'environment': env,
            "account_alias": account_alias,
            "nonprod_account_alias": account_alias
        }
    func_dict = get_native_dict(get_file_contents(jsonnet_functions_path))
    jsonnet_contents = get_file_contents(jsonnet_path)
    manifest_json = _jsonnet.evaluate_snippet(
        'manifest.jsonnet',
        jsonnet_contents,
        ext_vars={e.split('=')[0]:e.split('=')[1] for e in ext_var},
        tla_vars={e.split('=')[0]:e.split('=')[1] for e in tla_str},
        native_callbacks=func_dict
    )
    return json.loads(json.dumps(manifest_json))

@click.command()
@click.help_option()
@click.version_option()
@click.argument('path-to-jsonnet-file')
@click.option('--native-functions',show_default=True,help="Path to native functions python file. [Defaults to jsonnet_functions.py file in same folder as jsonnet file.]")
@click.option('--tla-str', multiple=True, help="Top level arguments to pass in to jsonnet file. Can be used multiple times.")
@click.option('--ext-var', multiple=True, help="External vars to pass in to jsonnet file. Can be used multiple times.")
def main(path_to_jsonnet_file, native_functions, tla_str, ext_var):
    json = render_jsonnet(path_to_jsonnet_file, native_functions, tla_str, ext_var)
    click.echo(json)