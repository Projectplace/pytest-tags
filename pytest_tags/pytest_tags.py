import pytest
import importlib


def pytest_configure(config):
    """
    py.test hook for test session configurations.

    :param config: py.test config module
    :return: None
    """

    # Object data setup marker
    config.addinivalue_line("markers",
                            "setup_data: test data for object creation")


def _get_representation(class_name, request):
    base = request.config.getini('representation_path').lower()
    module = importlib.import_module(base.replace('/', '.'))
    return getattr(module, class_name)


def pytest_addoption(parser):
    parser.addini('representation_path',
                  help='directory for representations')


@pytest.fixture(scope='module')
def test_db(request):
    """
    Creates a TestDataCollection instance which houses all the data representation objects.

    :param request: py.test request module
    :return: TestDataCollection instance
    """

    tdc = _get_representation("TestDataCollection", request)()

    yield tdc

    tdc.clear()


@pytest.fixture(scope='function', autouse=True)
def clean_test_db(request, test_db):
    """
    This will clear the TestDataCollection from all objects with a ttl of 'function'.

    :param request: py.test request module
    :param test_db: fixture test_db
    :return: None
    """
    yield

    test_db.clear(request.scope)


@pytest.fixture(scope='module', autouse=True)
def setup_module(request, test_db):
    """
    Module level object factory.

    This fixture sets up test data with a ttl of 'module'.

    :param request: py.test request module
    :param test_db: fixture test_db
    :return: None
    """
    if hasattr(request.module, 'module_setup_data'):
        _setup(request.module.module_setup_data, test_db, request)


@pytest.fixture(scope='function', autouse=True)
def setup_function(request, test_db):
    """
    Function level object factory.

    This fixture sets up test data with a ttl of 'function'.

    :param request: py.test request module
    :param test_db: fixture test_db
    :return: None
    """
    setup_data = request.node.get_marker('setup_data')

    if not setup_data:
        return

    _setup(request.function.setup_data.args, test_db, request)


def _setup(test_data, test_db, request):
    """
    Setup test data and add to test DB.

    :param test_data: test data for object creation
    :param test_db: test DB
    :param scope: ttl for created object(s)
    :return: None
    """
    def _add():
        test_db.add(created_obj, request.scope)
        # This adds objects created within an object creation to the test_db
        if hasattr(created_obj, 'default_representations'):
            representations = created_obj.default_representations
            if not isinstance(representations, list):
                raise RuntimeError("default_representations must return a list!")
            for each in _flatten_list(representations):
                test_db.add(each, request.scope)

    for data in test_data:
        for obj, params in data.items():
            obj_to_create = _get_representation(obj, request)
            if isinstance(params, list):  # if params is a list, that means we have multiple objects to create
                for sig in params:  # We must work on a copy of the data or else rerunfailures/flaky fails
                    created_obj = _create(obj_to_create, sig.copy(), test_db, request)
                    _add()
            else:
                created_obj = _create(obj_to_create, params.copy(), test_db, request)
                _add()


def _create(obj_to_create, test_params, test_db, request):
    """
    Create test data object (real object representation).

    :param obj_to_create: type of representation to create
    :param test_params: creation parameters
    :param test_db: test DB
    :param request: py.test request module
    :return: instance of created object
    """

    # object_param is the name of the param from representation objects create-function
    for object_param in obj_to_create.SIGNATURE.keys():

        # get the value from the signature provided by parametrize (by the test), if no value was specified
        # the value will be None
        test_param_value = test_params.get(object_param, None)

        # get the type of the param (object_param) from the signature
        object_param_type = obj_to_create.SIGNATURE[object_param]

        # if test_param_value and object_param_type is of the same type, usually (base)string, we continue
        if isinstance(test_param_value, object_param_type):
            continue
        # elif test_param_value is of type basestring, we get the object represented by object_param_type
        # and test_param_value
        elif isinstance(test_param_value, basestring):
            test_params[object_param] = _find_object(test_db, object_param_type, test_param_value)
        # else we remove the parameter because object_param defaults to None
        else:
            test_params.pop(object_param, None)

        # We can remove this when legacy is dead and gone! [JB 2017-01-12]
        if _is_legacy(obj_to_create, request):
            test_params['in_classic'] = True

    try:
        return obj_to_create.create(**test_params)
    except IndexError:  # Sometimes we get a 'Failue to persist' which causes a IndexError, so we retry once.
        from time import sleep
        sleep(5)
        return obj_to_create.create(**test_params)


def _is_legacy(obj, request):
    """
    Determine if an EnterpriseProject should be legacy/classic or harmony

    :param obj: Object to be created
    :param request: py.test request module
    :return: bool
    """
    if obj.__name__ == "EnterpriseProject":
        if request.scope == 'module' and hasattr(request.module, 'pytestmark'):
            if isinstance(request.module.pytestmark, list):
                if any("legacy" in marker.name for marker in request.module.pytestmark):
                    return True
            else:
                if request.module.pytestmark.name == "legacy":
                    return True
        if request.scope == 'function' and hasattr(request.function, 'legacy'):
            return True
    return False


def _find_object(test_db, object_type, value):
    """
    Due to some representations having an inheritance structure this functions finds the correct type in the test DB.

    :param test_db: test DB
    :param object_type:
    :param value: test DB object identifier
    :return: object representation instance from test DB
    """
    obj = test_db.get(object_type.__name__, value)
    if obj:
        return obj
    for class_type in object_type.__subclasses__():
        obj = test_db.get(class_type.__name__, value)
        if obj:
            return obj
    raise


def _flatten_list(representations):
    """
    The default_representation can sometimes be a list of lists, this flattens that list.

    :param representations: list of object representations
    :return: flattened list of representations
    """
    def flatten(l):
        for el in l:
            if isinstance(el, list):
                for sub in flatten(el):
                    yield sub
            else:
                yield el
    return list(flatten(representations))
