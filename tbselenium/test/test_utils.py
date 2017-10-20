import unittest
import tbselenium.utils as ut
from os.path import realpath
from os import environ


class UtilsTest(unittest.TestCase):
    def test_read_file(self):
        file_content = ut.read_file(realpath(__file__))
        self.assertIn('whatever written here', file_content)

    def test_prepend_to_env_var(self):
        env_var_name = "foo"
        value1 = "bar"
        value2 = "baz"

        environ[env_var_name] = value2
        ut.prepend_to_env_var(env_var_name, value1)
        self.assertEqual(environ[env_var_name], ":".join([value1, value2]))

        environ[env_var_name] = ""

        ut.prepend_to_env_var(env_var_name, value1)
        self.assertEqual(environ[env_var_name], value1)

        ut.prepend_to_env_var("non_existent_env_var", value1)
        self.assertEqual(environ["non_existent_env_var"], value1)


if __name__ == "__main__":
    unittest.main()
