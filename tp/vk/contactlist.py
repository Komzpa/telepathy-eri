import dbus
from telepathy.server import ConnectionInterfaceContactList, ConnectionInterfaceContactGroups
import telepathy
import vkcom
import gobject
from vkcom.messenger import ContactList

__author__ = 'eri'

import logging
from utils.decorators import loggit

logger = logging.getLogger('Eri.Vk/list')

import channelmanager

class VkContactList(
    ConnectionInterfaceContactList,
    ConnectionInterfaceContactGroups
):

    _contact_list_state = telepathy.CONTACT_LIST_STATE_NONE
    _contact_list_persists = False
    _can_change_contact_list = False
    _request_uses_message = True
    _download_at_connection = True
    _group_storage = telepathy.CONTACT_METADATA_STORAGE_TYPE_SUBSCRIBED

    def __init__(self):

        ConnectionInterfaceContactList.__init__(self)
        ConnectionInterfaceContactGroups.__init__(self)



    @loggit(logger)
    def _contacts_changed(self):
        changes = dbus.Dictionary(signature='u(uus)')
        identifiers = dbus.Dictionary(signature='us')
        removals = dbus.Dictionary(signature='us')

        for contact in self._friends:
            handle = self.ensure_contact_handle(contact)
            changes[handle] = dbus.Struct((True, True, ''), signature='uus')
            identifiers[handle] = handle.name

        self.ContactsChangedWithID(changes, identifiers, removals)
        self.ContactsChanged(changes, dbus.Array([], signature='u')) #deprecated



    @loggit(logger)
    def Download(self):
        self.ContactListStateChanged(telepathy.CONTACT_LIST_STATE_WAITING)
        try:
            friendlists = self.Api.friends.get(fields='nickname,screen_name,photo_50,online').get('items',[])
            friends = ContactList(self.Api.friends,fields='nickname,screen_name,photo_50,online',items=friendlists)
            self.contact_list.cl.update(friends.cl)
            self._groups = self.Api.friends.getLists()
            self._friends = friends.cl.values()

        except vkcom.APIError,e:
            self.ContactListStateChanged(telepathy.CONTACT_LIST_STATE_FAILURE)
            raise e

        props = self._generate_props(telepathy.CHANNEL_TYPE_CONTACT_LIST,
                self._self_handle, False, self._self_handle)

        self._channel_manager.channel_for_props(props,signal=True)

        gobject.idle_add(self._contacts_changed)
        self.ContactListStateChanged(telepathy.CONTACT_LIST_STATE_SUCCESS)


    def GetContactAttributes(self, handles, Interfaces, Hold):
        ret = super(VkContactList,self).GetContactAttributes(handles,Interfaces,Hold)
        for handle_id in ret.keys():
            if ret[handle_id][telepathy.CONN_INTERFACE + '/contact-id'] in self._friends:
                ret[handle_id][telepathy.CONNECTION_INTERFACE_CONTACT_LIST+'/subscribe'] = telepathy.SUBSCRIPTION_STATE_YES
                ret[handle_id][telepathy.CONNECTION_INTERFACE_CONTACT_LIST+'/publish'] = telepathy.SUBSCRIPTION_STATE_YES
            else:
                ret[handle_id][telepathy.CONNECTION_INTERFACE_CONTACT_LIST+'/publish'] = telepathy.SUBSCRIPTION_STATE_NO
                ret[handle_id][telepathy.CONNECTION_INTERFACE_CONTACT_LIST+'/subscribe'] = telepathy.SUBSCRIPTION_STATE_NO

        return ret

    @loggit(logger)
    def GetContactListAttributes(self, Interfaces, Hold):
        handles = []
        groups = {}

        logger.info(repr(self._groups))

        for contact in self._friends:
            handle = self.ensure_contact_handle(contact)
            handles.append(int(handle))
            groups[int(handle)] = contact.get('lists',[])

        ret = self.GetContactAttributes(handles,Interfaces,Hold)

        for handle_id in ret.keys():
            lists = [lst['name'] for lst in self._groups if lst['list_id'] in groups[handle_id]] or ['vk']
            ret[handle_id][telepathy.CONNECTION_INTERFACE_CONTACT_GROUPS + '/groups'] = dbus.Array(lists,signature='s')

        return ret

    def _get_groups(self):
        return [lst['name'] for lst in self._groups]+['vk']

    @loggit(logger)
    def friend_offline(self,uid,reason=1):
        handle = self.ensure_contact_handle(uid)
        handle.contact['online'] = 0
        presence = self.GetPresences([handle.id])[handle.id]
        # self.PresencesChanged(presence)

    @loggit(logger)
    def friend_online(self,uid):
        handle = self.ensure_contact_handle(uid)
        handle.contact['online'] = 1
        presence = self.GetPresences([handle.id])[handle.id]
        # self.PresencesChanged(presence)