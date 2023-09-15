import version9 as v9
import pandas as pd
import numpy as np
import datetime
from ifcopenshell import guid



def systype(elem):
    systy = v9.systemType()
    systy.set_href(elem)


def ids_value(elem):
    ids_val = v9.idsValue()
    ids_val.set_simpleValue(elem)
    return ids_val


def entityType(name):
    entityTy = v9.entityType()
    entityTy.set_name(ids_value(name))
    return entityTy


def pset_app(dframe, sp_name, elem, entity, uobj, pset, property, value, measure):
    props = []
    propset = dframe.loc[(dframe[sp_name] == elem) & (dframe[entity] == uobj), pset]
    unique_pset = np.unique(propset)
    for a in unique_pset:
        prop = dframe.loc[dframe[pset] == a, [property]]
        unique_prop = np.unique(prop)
        for p in unique_prop:
            val = dframe.loc[dframe[property] == p, [value]]
            unique_val = np.unique(val)
            print('****************')
            for k in unique_val:
                unique_mes = np.unique(dframe.loc[dframe[value] == k, [measure]])
                propi = v9.propertyType()
                propi.set_propertySet(ids_value(a))
                propi.set_name(ids_value(p))
                if unique_val.all():
                    propi.set_value(ids_value(k))
                props.append(propi)
                propi.set_datatype(unique_mes[0])
    return(props)


def pset_requ(dframe, sp_name, elem, entity, uobj, pset, property, value, measure):
    props = []
    propset = dframe.loc[(dframe[sp_name] == elem) & (dframe[entity] == uobj), pset]
    unique_pset = np.unique(propset)
    for a in unique_pset:
        prop = dframe.loc[dframe[pset] == a, [property, value, measure]]
        print(prop)
        for i, j in prop.iterrows():
            prop = v9.propertyType5()
            #prop = v9.propertyType()
            prop.set_propertySet(ids_value(a))
            prop.set_name(ids_value(j[property]))
            test_val = dframe.loc[dframe[pset] == a, value]
            if test_val.all():
                prop.set_value(ids_value(j[value]))
            prop.set_minOccurs("1")
            prop.set_maxOccurs(1)
            prop.set_datatype(j[measure])
            props.append(prop)
    return(props)


def define_info(dframe, infT, root):
    if dframe['title'].iloc[0] != '':
        infT.set_title(dframe['title'].iloc[0])
    else:
        infT.set_title("Default")

    if dframe['copyright'].iloc[0] != '':
        infT.set_copyright(dframe['copyright'].iloc[0])
    else:
        pass

    if dframe['version'].iloc[0] != '':
        infT.set_version(dframe['version'].iloc[0])
    else:
        pass
    
    if dframe['description'].iloc[0] != '':
        infT.set_description(dframe['description'].iloc[0])
    else:
        pass
        
    if dframe['author'].iloc[0] != '':
        infT.set_author(dframe['author'].iloc[0])
    else:
        pass
    
    infT.set_date(datetime.date.today())

    if dframe['purpose'].iloc[0] != '':
        infT.set_purpose(dframe['purpose'].iloc[0])
    else:
        pass
    
    if dframe['milestone'].iloc[0] != '':
        infT.set_milestone(dframe['milestone'].iloc[0])
    else:
        pass

    root.set_info(infT)


class writer:
    def write(self, stri):
        print(stri, end='')


class file_writer:
    def __init__(self, filename):
        self.file = open(filename, 'w')

    def write(self, stri):
        self.file.write(stri)

    def __del__(self):
        self.file.close()


def specification_entity(dframe, elem, uobj, specs):   
    spec = v9.specificationType()
    spec.set_name(name = elem)
    ifc_obj = dframe.loc[dframe['specification_name'] == elem, 'ifc_version']
    ifc_version = np.unique(ifc_obj)
    spec.set_ifcVersion(ifcVersion = ifc_version[0])
    spec.set_minOccurs("1")
    spec.set_maxOccurs(1)
    spec.set_identifier(guid.new())
    spec.set_applicability(applicability(dframe, elem, uobj))
    spec.set_requirements(requirements(dframe, elem, uobj))
    if dframe.loc[dframe['specification_name'] == elem, 'description_spec'].any():
        val = np.unique(dframe.loc[dframe['specification_name'] == elem, 'description_spec'])
        print(val[0])
        spec.set_description(val[0])
    specs.append(spec)


def applicability(dframe, elem, uobj):
    app = v9.applicabilityType()
    app.set_entity(entityType(uobj))
    obj_class_val = dframe.loc[dframe['specification_name'] == elem, 'classification_value_ap']
    if obj_class_val.any():
        obj_class_val = obj_class_val.astype(str)
        unique_class_val = np.unique(obj_class_val)
        for j in unique_class_val:
            class_obj = v9.classificationType()
            class_obj.set_value(ids_value(j))
            class_obj.set_system(ids_value(j))
        app.set_classification([class_obj])
    else:
        pass

    obj_attnam = dframe.loc[dframe['specification_name'] == elem, 'attribute_name_ap']
    unique_obj_name = np.unique(obj_attnam)
    if unique_obj_name.any():
        att = v9.attributeType()
        att.set_name(ids_value(unique_obj_name))
    
    obj_attval = dframe.loc[dframe['specification_name'] == elem, 'attribute_value_ap']
    unique_obj_val = np.unique(obj_attval)
    if unique_obj_val.any():
        att.set_value(ids_value(unique_obj_val))
        app.set_attribute([att])

    pre_test = dframe.loc[dframe['specification_name'] == elem, 'propertyset_ap']
    unique_pretest = np.unique(pre_test)
    if unique_pretest.any():
        app.set_property(pset_app(dframe, 'specification_name', elem, 'entity_name_ap', uobj, 'propertyset_ap', 'property_name_ap', 'property_value_ap', 'measure_ap'))


    obj_materil = dframe.loc[dframe['specification_name'] == elem, 'material_value_ap']
    unique_mat = np.unique(obj_materil)
    if unique_mat.any():
        for t in obj_materil:
            mat = v9.materialType()
            mat.set_value(ids_value(t)) 
        app.set_material(mat)

    return app


def requirements(dframe, elem, uobj): 
    requ = v9.requirementsType()
    requ.set_entity([entityType(uobj)])
    req_class_val = dframe.loc[dframe['specification_name'] == elem, 'classification_value']
    if req_class_val.all():
        req_class_val= req_class_val.astype(str)
        unique_class_val = np.unique(req_class_val)
        for req_el in unique_class_val:
            class_obj_req = v9.classificationType6() 
            class_obj_req.set_value(ids_value(req_el))

    req_class_sys = dframe.loc[dframe['specification_name'] == elem, 'classification_system']
    unique_class_sys = np.unique(req_class_sys)
    if unique_class_sys.all():
        for e in unique_class_sys:
            class_obj_req.set_system(ids_value(e))

        class_obj_req.set_instructions('TO_DO')
        requ.set_classification([class_obj_req])

    req_attnam = dframe.loc[dframe['specification_name'] == elem, 'attribute_name']
    if req_attnam.all():
        for d in req_attnam:
            att = v9.attributeType()
            att.set_name(ids_value(d))

        requ.set_attribute([att])

    pre_test_req = dframe.loc[dframe['specification_name'] == elem, 'propertyset']
    unique_pretest_req = np.unique(pre_test_req)
    if unique_pretest_req.any():
        requ.set_property(pset_requ(dframe, 'specification_name', elem, 'entity_name', uobj, 'propertyset', 'property_name', 'property_value', 'measure'))


    req_materil = dframe.loc[dframe['specification_name'] == elem, 'material_value']
    if req_materil.all():
        for t in req_materil:
            mat = v9.materialType()
            mat.set_value(ids_value(t)) 
        requ.set_material([mat])

    return requ
   

def read_file(file):
    n = 1
    dframe = pd.read_csv(file, sep=';', skipinitialspace= True, skiprows=2, encoding = 'utf-8', keep_default_na=False)
    root = v9.ids()
    infT = v9.infoType()
    define_info(dframe, infT, root)
    spec_ty = v9.specificationsType()
    specs = []
    unique_elem = np.unique(dframe.loc[:, 'specification_name'])
    for elem in unique_elem:
        ent_obj = dframe.loc[dframe['specification_name'] == elem, 'entity_name_ap']
        if ent_obj.empty == False:
            ent_obj = ent_obj.astype(str)
            unique_obj = np.unique(ent_obj)
            for uobj in unique_obj:
                specification_entity(dframe, elem, uobj, specs)
        else:
            pass
            
            
    spec_ty.set_specification(specs)
    root.set_specifications(spec_ty)
    root.export(file_writer("test.xml"),0)


#######################################
#AUSFÜHRUNG
#######################################


if __name__ == '__main__':
    file = 'test.csv'
    test = read_file(file)