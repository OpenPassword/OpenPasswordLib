from mock import patch
from nose.tools import *

from openpassword._keychain import Keychain
from openpassword.abstract import DataSource
from openpassword.exceptions import NonInitialisedKeychainException, KeychainAlreadyInitialisedException


class KeychainSpec:
    def it_is_created_locked(self):
        keychain = self._get_simple_keychain()
        eq_(keychain.is_locked(), True)

    def it_unlocks_the_keychain_with_the_right_password(self):
        keychain = self._get_simple_keychain()
        keychain.unlock('rightpassword')
        eq_(keychain.is_locked(), False)

    def it_is_iterable_as_list_of_items_when_unlocked(self):
        keychain = self._get_simple_keychain()
        keychain.unlock("righpassowrd")

        try:
            iter(keychain)
        except TypeError:
            raise AssertionError("Keychain is not iterable")

    def it_locks_the_keychain(self):
        keychain = self._get_simple_keychain()
        keychain.unlock('rightpassword')
        eq_(keychain.is_locked(), False)

        keychain.lock()
        eq_(keychain.is_locked(), True)

    @raises(NonInitialisedKeychainException)
    def it_raises_NonInitialisedKeychainException_when_unlocking_uninitialized_keychain(self):
        keychain = self._get_non_initialised_keychain()
        keychain.unlock("somepassword")

    def it_is_initialisable_using_a_password(self):
        keychain = self._get_non_initialised_keychain()
        keychain.initialise("somepassword")
        eq_(keychain.is_initialised(), True)

    def it_keeps_uninitialised_if_we_dont_initialise_it(self):
        keychain = self._get_non_initialised_keychain()
        eq_(keychain.is_initialised(), False)

    @patch.object(DataSource, "initialise")
    def it_delegates_initialisation_to_the_data_source(self, data_source):
        keychain = Keychain(data_source)
        keychain.initialise("somepassword")

        assert data_source.initialise.called is True

    @patch.object(DataSource, "add_item")
    def it_delegates_item_creation_to_the_data_source(self, data_source):
        keychain = Keychain(data_source)
        keychain.append({"id": "someitem_id"})

        assert data_source.add_item.called is True

    def it_is_created_initialised_for_an_initialised_data_source(self):
        keychain = self._get_simple_keychain()
        eq_(keychain.is_initialised(), True)

    @patch.object(DataSource, 'is_keychain_initialised')
    def it_is_created_non_initialised_for_a_non_initialised_data_source(self, data_source):
        data_source.is_keychain_initialised.return_value = False

        keychain = Keychain(data_source)
        eq_(keychain.is_initialised(), False)

    @raises(KeychainAlreadyInitialisedException)
    def it_throws_keychainalreadyinitialisedexception_if_initialising_an_already_initialised_keychain(self):
        keychain = self._get_simple_keychain()
        keychain.initialise("somepassword")

    def it_adds_the_item_to_the_keychain_with_the_item_id_as_key(self):
        keychain = self._get_simple_keychain()
        item = {'id': 'new_item_id'}
        keychain.append(item)
        eq_(keychain['new_item_id'], item)

    def it_allows_for_items_to_be_appended(self):
        keychain = self._get_simple_keychain()
        new_item = {"id": "new_item"}
        keychain.append(new_item)
        eq_(new_item in keychain, True)

    def _get_non_initialised_keychain(self):
        keychain = self._get_simple_keychain()
        keychain.initialised = False
        return keychain

    @patch.object(DataSource, 'is_keychain_initialised')
    def _get_simple_keychain(self, data_source):
        data_source.is_keychain_initialised.return_value = True

        return Keychain(data_source)
