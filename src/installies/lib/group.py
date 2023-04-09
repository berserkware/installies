class Group:
    """
    A class for getting multiple objects from the database.

    This is a base class that needs to be inherited to work. The derivitive of the class
    should put a list of all the getter classes in the 'getters' attribute. The derivitive
    classes also need to add a database model in the 'model' attribute.
    
    The object are got by getter classes that have a method named 'get' that takes
    a SelectQuery object and other kwargs. The method should return the SelectQuery.
    The kwargs are the params to get the objects from. The kwargs are sent by the user,
    so they should be treated carefully.
    """

    getters = []
    model = None

    @classmethod
    def get(cls, **kwargs):
        """
        Gets a group of objects from the database.

        It uses the getter classes in the 'getter' attribute. If the model in
        the `model` attribute is non, then an empty list is returned.
        """

        if cls.model is None:
            return []

        objects = cls.model.select()

        for getter in cls.getters:
            objects = getter.get(objects, **kwargs)

        return objects

        
