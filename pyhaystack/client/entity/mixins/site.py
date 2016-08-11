#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
'site' related mix-ins for high-level interface.
"""

import hszinc

class SiteMixin(object):
    """
    A mix-in used for entities that carry the 'site' marker tag.
    """

    def find_entity(self, filter_expr=None, single=False,
            limit=None, callback=None):
        """
        Retrieve the entities that are linked to this site.
        This is a convenience around the session find_entity method.
        """
        site_ref = hszinc.dump_scalar(self.id)
        if filter_expr is None:
            filter_expr = 'siteRef==%s' % site_ref
        else:
            filter_expr = '(siteRef==%s) and (%s)' % (site_ref, filter_expr)
        return self._session.find_entity(filter_expr, limit, single, callback)


    def __getitem__(self,key):
        # Using [key] syntax on a site allow to retrieve a tag directly
        # or an equipment referred to this particular site
        for each in self.tags:
            if key == each:
                return self.tags[key]
        # if key not found in tags... we probably are searching an equipment
        # self will call __iter__ which will look for equipments
        for each in self:
            # Given an ID.... should return the equip with this ID
            if key.replace('@','') == str(each.id).replace('@',''):
                return each
            # Given a dis or navName... should return equip
            elif key == each.tags['dis'] or key == each.tags['navName']:
                return each
            # Given a partial dis or nav... raise an error with a hint
            # Will need to think about that... make things go bad for things
            # with similar names
            #elif key in each.tags['dis'] or key in each.tags['navName']:
            #    raise KeyError('Wrong equipment name. Do you mean "%s" ?' % each.tags['dis'])
        request = self.find_entity(key)
        return request.result

    def __iter__(self):
        """
        When iterating over a site, we iterate equipments.
        """
        for equip in self.equipments:
            yield equip
            
    @property
    def equipments(self):
        """
        First read will force a request and create local list
        """
        try:
            # At first, this variable will not exist... will be created
            return self._list_of_equip
        except AttributeError:
            print('Reading equipments for this site...')
            self._add_equip()
            return self._list_of_equip
            
    def refresh(self):
        """
        Re-create local list of equipments
        """
        self._list_of_equip = []
        self._add_equip()
        
    def _add_equip(self):
        """
        Store a local copy of equip for this site
        To accelerate browser
        """
        if not '_list_of_equip' in self.__dict__.keys():
            self._list_of_equip = []       
        for equip in self['equip'].items():
            self._list_of_equip.append(equip[1])
        

class SiteRefMixin(object):
    """
    A mix-in used for entities that carry a 'siteRef' reference tag.
    """

    def get_site(self, callback=None):
        """
        Retrieve an instance of the site this entity is linked to.
        """
        return self._session.get_entity(self.tags['siteRef'],
                callback=callback, single=True)
