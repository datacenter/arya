#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python APIC Rest Adapter (pyra)

Joseph LeClerc - jolecler@cisco.com

Copyright (C) 2016 Cisco Systems Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Converts cobra code into equivalent blocks of APIC XML/JSON.
"""

import json
import lxml.etree as ElementTree
from cobra.internal.codec.jsoncodec import toJSONStr
from cobra.internal.codec.xmlcodec import toXMLStr
import cobra.model.fv
import cobra.model.pol

__author__ = "Joseph LeClerc"
__copyright__ = "Copyright (C) 2016 Cisco Systems Inc."
__license__ = "Apache 2.0"
__version__ = "1.1.0"
__maintainter__ = "Joseph LeClerc"
__email__ = "jolecler@cisco.com"
__status__ = "Production"

def main():
    """Use locals() to create a PyraTree, then get JSON/XML representations of the PyraTree data and print them."""
    # Put Arya-generated code here
    polUni = cobra.model.pol.Uni('')
    fvTenant = cobra.model.fv.Tenant(polUni, 'pod1')

    # Create the tree
    tree = PyraTree('polUni', locals())

    # Acquire a copy of the tree to use, e.g to save/modify/post.
    dict_tree = tree.dtree
    xml_tree = tree.etree
    json_tree = tree.jtree

    # Example output
    print ElementTree.tostring(xml_tree, encoding='utf-8')
    print json.dumps(json_tree, indent=4, sort_keys=True)

class PyraTree(object):
    """A tree of PyraTreeNode objects, which represent the MO's."""
    def __init__(self, root_var, mylocals):
        """:param rmap: locals() is reversed to optimize lookup of variable names given Cobra objects."""
        mylocals = mylocals.copy()
        rmap = {v:k for k,v in mylocals.items() if isinstance(v, cobra.mit.mo.Mo)}
        self._root = PyraTreeNode(mylocals[root_var], rmap)

    def _dtree(self):
        """Return a dictionary Tree."""
        tree = {'tag': self.root.tag, 'attrib': self.root.attrib, 'children': {}}
        def recurse_tree(parent, parentdict):
            """Recursively build a hierarchy of variable names, their config properties, and their children according to their MO relationships."""
            for child in parent.children:
                child_dict = {'tag': child.tag, 'attrib': child.attrib, 'children': {}}
                parentdict[child.name]= child_dict
                recurse_tree(child, child_dict['children'])
        recurse_tree(self.root, tree['children'])
        return {self.root.name: tree}

    def _etree(self):
        """Return an element Tree (XML Tree). 
        Shows MO dn's because it uses PyraTreeNode methods."""
        et_root = ElementTree.Element(self.root.tag, self.root.attrib)
        def recurse_tree(parent, et_parent):
            """Recursively build a full XML ElementTree rooted on 'parent'"""
            for child in parent.children:
                et_child = ElementTree.Element(child.tag, child.attrib)
                et_parent.append(et_child)
                recurse_tree(child, et_child)
        recurse_tree(self.root, et_root)
        return ElementTree.ElementTree(et_root)

    def _etree_cobra(self):
        """Return an XML tree via the Cobra implementation."""
        return ElementTree.fromstring(toXMLStr(self.root.mo))

    def _jtree(self):
        """Return a json tree via the Cobra implementation."""
        return json.loads(toJSONStr(self.root.mo))

    @property
    def dtree(self):
        """Dictionary Tree.
        :return: A representation of this tree as a dictionary.
        :rtype: dict"""
        return self._dtree()
    @property
    def etree(self):
        """XML Tree.
        :return: A fully-populated XML ElementTree.
        :rtype: xml.etree.ElementTree.ElementTree"""
        return self._etree()
    @property
    def jtree(self):
        """JSON Tree.
        :return: A representation of this tree as JSON.
        :rtype: json"""
        return self._jtree()
    @property
    def root(self):
        """
        :return: The root element of this tree.
        :rtype: PyraTreeNode"""
        return self._root

class PyraTreeNode(object):
    """A wrapper for Cobra API Mo objects."""
    def __init__(self, mo, reverse_locals_map):
        """:param reverse_locals_map: mapping of objects to their variable names. Allows lookup of the name of the "mo" object. It is locals() with the keys and values swapped."""
        self._rmap = reverse_locals_map
        self._name = reverse_locals_map[mo]
        self._mo = mo

    @property
    def attrib(self):
        """ Note: this only shows "config" attributes (attributes for which the MO's propMeta "isconfig" property is equal to True - for examples, see the Cobra files for any configurable MO.)
        :return: A dictionary of attributes:values for this MO. Also includes "distinguished name" (dn).
        :rtype: dict"""
        return dict({x.name: getattr(self.mo, x.name) for x in self.mo.meta.props if x.isConfig and hasattr(self.mo, x.name)}, **{'dn': self.dn})
    @property
    def children(self):
        """
        :return: A list of the children of this node (as PyraTreeNode objects)
        :rtype: list"""
        return [PyraTreeNode(child, self._rmap) for child in self.mo.children]
    @property
    def classname(self):
        """
        :return: The name of the Python class; i.e "LDevVip" rather than "vnsLDevVip."
        :rtype: str"""
        return type(self.mo).__name__
    @property
    def dn(self):
        """
        :return: The dn of the Mo, as it would appear in XML/JSON.
        :rtype: str"""
        return str(self.mo.dn)
    @property
    def mo(self):
        """
        :return: This instance's internal Mo object.
        :rtype: cobra.mit.mo.Mo"""
        return self._mo
    @property
    def name(self):
        """
        :return: The name of the variable used to create this instance, e.g "vnsLDevVip2".
        :rtype: str"""
        return self._name
    @property
    def tag(self):
        """
        :return: The moClassName of the object's metaclass (which is also the XML tag.)
        :rtype: str"""
        return reduce(getattr, [self.mo, 'meta', 'moClassName'])

if __name__ == '__main__':
    main()
