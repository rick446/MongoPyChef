import sys

from ming import schema as S

from formencode import validators as fev

from .. import model as M

class CookbookNumVersions(fev.Int):

    def _to_python(self, value, state):
        if value == 'all':
            return sys.maxint
        return super(CookbookNumVersions, self)._to_python(value, state)

class JSONSchema(fev.FancyValidator):

    def __init__(self, fields, **kwargs):
        self.schema = S.Object(fields, **kwargs)

    def _from_python(self, value, state):
        return value

    def _to_python(self, value, state):
        try:
            return self.schema.validate(value)
        except S.Invalid, inv:
            raise self._to_formencode_invalid(inv)

    @classmethod
    def _to_formencode_invalid(cls, ming_invalid):
        if ming_invalid.error_dict:
            return fev.Invalid(
                ming_invalid.msg, 
                ming_invalid.value, ming_invalid.state,
                error_dict=dict(
                    (k, cls._to_formencode_invalid(v))
                    for k,v in ming_invalid.error_dict.items()))
        elif ming_invalid.error_list:
            return fev.Invalid(
                ming_invalid.msg, 
                ming_invalid.value, ming_invalid.state,
                error_list=map(cls._to_formencode_invalid, ming_invalid.error_list))
        else:
            return fev.Invalid(
                ming_invalid.msg, 
                ming_invalid.value, ming_invalid.state)

    @classmethod
    def jsonify_invalid(cls, err):
        d = dict(msg=err.msg)
        if err.error_dict:
            d['error_dict'] = dict(
                (k, cls.jsonify_invalid(v))
                for k,v in err.error_dict.items())
        elif err.error_list:
            d['error_list'] = map(cls.jsonify_invalid, err.error_list)
        return d
        
class JSONModelSchema(JSONSchema):
    model_class=None
    chef_type=None
    json_class=None
    include_fields=[]
    exclude_fields=[]
    extra_fields={}

    def __init__(self):
        d = dict(
            chef_type=self.chef_type,
            json_class=self.json_class)
        for f in self.model_class.m.fields:
            if self.include_fields:
                if f.name in self.include_fields:
                    d[f.name] = f.schema
            elif f.name not in self.exclude_fields:
                d[f.name] = f.schema
        d.update(self.extra_fields)
        super(JSONModelSchema, self).__init__(d)

class CookbookVersionSchema(JSONModelSchema):
    model_class=M.cookbook_version
    chef_type='cookbook_version'
    json_class='Chef::CookbookVersion'
    exclude_fields=['_id', 'account_id' ]
    extra_fields={'frozen?': bool }

class EnvironmentSchema(JSONModelSchema):
    model_class=M.environment
    chef_type='environment'
    json_class='Chef::Environment'
    exclude_fields=['_id', 'account_id']
    extra_fields=dict(
        default_attributes={str:None},
        override_attributes={str:None})
    
class NodeSchema(JSONModelSchema):
    model_class=M.node
    chef_type='node'
    json_class='Chef::Node'
    exclude_fields=['_id', 'account_id']
    extra_fields=dict(
        default={str:None},
        normal={str:None},
        override={str:None},
        automatic={str:None})

class RoleSchema(JSONModelSchema):
    model_class=M.role
    chef_type='role'
    json_class='Chef::Role'
    exclude_fields=['_id', 'account_id']

DatabagItemSchema = JSONSchema(
    dict(
        chef_type='data_bag_item',
        json_class='Chef::DataBagItem',
        name=str,
        data_bag=str,
        raw_data={ str: None }))
    
EnvironmentCookbookVersionsSchema = JSONSchema(dict(run_list=[str]))
