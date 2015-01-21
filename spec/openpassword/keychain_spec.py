from unittest.mock import patch
from nose.tools import raises

from openpassword._keychain import Keychain
from openpassword.abstract import DataSource, Item
from openpassword.exceptions import NonInitialisedKeychainException, KeychainAlreadyInitialisedException, \
    IncorrectPasswordException, KeychainLockedException, UnauthenticatedDataSourceException


class KeychainSpec:
    # Initialisation

    @patch("openpassword.abstract.DataSource")
    def it_is_initialisable_using_a_password(self, data_source):
        keychain = Keychain(data_source)
        keychain.initialise("somepassword")

        data_source.initialise.assert_called()

    @patch("openpassword.abstract.DataSource")
    def it_passes_initialisation_configuraton_to_data_source(self, data_source):
        password = "somepassword"
        config = {"iterations": 10}
        keychain = Keychain(data_source)
        keychain.initialise(password, config)

        data_source.initialise.assert_called_with(password, config)

    @patch("openpassword.abstract.DataSource")
    def it_remains_uninitialised_if_not_initialised(self, data_source):
        data_source.is_initialised.return_value = False
        keychain = Keychain(data_source)

        assert keychain.is_initialised() is False

    @patch("openpassword.abstract.DataSource")
    def it_delegates_initialisation_to_the_data_source(self, data_source):
        keychain = Keychain(data_source)
        keychain.initialise("somepassword")

        assert data_source.initialise.called is True

    @patch("openpassword.abstract.DataSource")
    def it_is_created_initialised_for_an_initialised_data_source(self, data_source):
        data_source.is_initialised.return_value = True
        keychain = Keychain(data_source)

        assert keychain.is_initialised() is True

    @patch("openpassword.abstract.DataSource")
    def it_is_created_non_initialised_for_a_non_initialised_data_source(self, data_source):
        data_source.is_initialised.return_value = False

        keychain = Keychain(data_source)

        assert keychain.is_initialised() is False

    @patch("openpassword.abstract.DataSource")
    @raises(KeychainAlreadyInitialisedException)
    def it_throws_if_initialising_existing_keychain(self, data_source):
        data_source.is_initialised.return_value = True
        keychain = Keychain(data_source)
        keychain.initialise("somepassword")

    # Unlocking

    @patch("openpassword.abstract.DataSource")
    def it_is_locked_if_the_data_source_has_not_been_authenticated(self, data_source):
        data_source.is_authenticated.return_value = False
        keychain = Keychain(data_source)

        assert keychain.is_locked() is True

    @patch("openpassword.abstract.DataSource")
    def it_is_unlocked_if_the_data_source_has_been_authenticated(self, data_source):
        data_source.is_authenticated.return_value = True
        keychain = Keychain(data_source)

        assert keychain.is_locked() is False

    @patch("openpassword.abstract.DataSource")
    def it_locks_itself_by_deauthenticating_the_data_source(self, data_source):
        keychain = Keychain(data_source)

        data_source.deauthenticate.assert_called()

    @patch("openpassword.abstract.DataSource")
    def it_unlocks_the_keychain_with_the_right_password(self, data_source):
        keychain = Keychain(data_source)
        keychain.unlock('rightpassword')

        data_source.authenticate.assert_called_with('rightpassword')

    @patch("openpassword.abstract.DataSource")
    @raises(IncorrectPasswordException)
    def it_throws_if_unlocking_with_incorrect_password(self, data_source):
        data_source.authenticate.side_effect = IncorrectPasswordException

        keychain = Keychain(data_source)
        keychain.unlock("wrongpassword")

    @patch("openpassword.abstract.DataSource")
    @raises(NonInitialisedKeychainException)
    def it_throws_if_unlocking_uninitialized_keychain(self, data_source):
        data_source.is_initialised.return_value = False
        keychain = Keychain(data_source)

        keychain.unlock("somepassword")

    # Item access

    @patch("openpassword.abstract.DataSource")
    def it_is_iterable_as_list_of_items_when_unlocked(self, data_source):
        data_source.is_authenticated.return_value = True
        keychain = Keychain(data_source)

        try:
            iter(keychain)
        except TypeError:
            raise AssertionError("Keychain is not iterable")

    @patch("openpassword.abstract.DataSource")
    @raises(KeychainLockedException)
    def it_is_not_iterable_as_list_of_items_when_locked(self, data_source):
        data_source.is_authenticated.return_value = False
        keychain = Keychain(data_source)

        iter(keychain)

    @patch("openpassword.abstract.Item")
    @patch("openpassword.abstract.DataSource")
    def it_gets_items_by_id_from_data_source(self, data_source, item):
        data_source.is_initialised.return_value = True
        data_source.is_authenticated.return_value = True
        data_source.get_item_by_id.return_value = item

        keychain = Keychain(data_source)

        assert keychain[item.get_id()] == item

    # Creating items

    @patch("openpassword.abstract.Item")
    @patch("openpassword.abstract.DataSource")
    def it_delegates_creating_items_to_the_data_source(self, data_source, item):
        data_source.create_item.return_value = item
        keychain = Keychain(data_source)

        assert keychain.create_item() == item

    # Saving items

    @patch("openpassword.abstract.DataSource")
    @raises(KeychainLockedException)
    def it_throws_if_adding_items_to_a_locked_keychain(self, data_source):
        data_source.save_item.side_effect = UnauthenticatedDataSourceException

        keychain = Keychain(data_source)
        keychain.save_item({"id": "someitem_id"})

    @patch("openpassword.abstract.DataSource")
    @raises(KeychainLockedException)
    def it_throws_if_gettings_items_from_a_locked_keychain(self, data_source):
        data_source.is_authenticated.return_value = False

        keychain = Keychain(data_source)
        keychain['ABC']

    @patch("openpassword.abstract.Item")
    @patch("openpassword.abstract.DataSource")
    def it_delegates_saving_items_to_the_data_source(self, data_source, item):
        keychain = Keychain(data_source)
        keychain.save_item(item)

        data_source.save_item.assert_called_with(item)

    # Changing password

    @patch("openpassword.abstract.DataSource")
    @raises(KeychainLockedException)
    def it_throws_if_setting_password_on_a_locked_keychain(self, data_source):
        data_source.is_authenticated.return_value = False
        keychain = Keychain(data_source)

        keychain.set_password("foobar")

    @patch("openpassword.abstract.DataSource")
    def it_changes_password(self, data_source):
        data_source.authenticate.return_value = None
        data_source.set_password.return_value = None

        keychain = Keychain(data_source)
        keychain.unlock("password")
        keychain.set_password("foobar")

        data_source.set_password.assert_called_with("foobar")
