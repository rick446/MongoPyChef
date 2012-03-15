import re

from .. import model as M

re_runlist_entry = re.compile(
    r'^(recipe|role)\[(.*)\]$')

def expand_runlist(account_id, runlist, env=None, seen=None):
    '''Given a runlist, return a list of cookbooks needed to satisfy it.'''
    if seen is None: seen = set()
    for entry in runlist:
        mo = re_runlist_entry.match(entry)
        if mo is None:
            type, id = 'recipe', entry
        else:
            type, id = mo.groups()
        if type == 'role':
            r = M.Role.query.get(account_id=account_id, name=id)
            sub_list = r.env_run_lists.get(env.name, r.run_list)
            for cb in expand_runlist(account_id, sub_list, env.name, seen):
                yield cb
        elif type == 'recipe':
            cb = id.split('::')[0]
            if cb in seen: continue
            seen.add(cb)
            cb_filter = dict(
                account_id=account_id,
                cookbook_name=cb)
            if '@' in cb:
                cb, version = cb.split('@')
                cb_filter.update(
                    cookbook_name=cb,
                    version=version)
            versions = M.CookbookVersion.query.find(cb_filter).all()
            versions = sorted(versions, key=lambda cb:cb.version_vector, reverse=True)
            if env is not None:
                versions = env.filter_versions(cb, versions)
            versions = list(versions)
            for v in versions:
                yield v
        
