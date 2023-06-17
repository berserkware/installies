from installies.lib.validate import ValidationError

class FormInput:
    """
    A class for storing data about inputs from forms.

    :param name: The name of the input in the post data.
    :param validator: The validator class to validate the data.
    :param converter: A callable to convert the data to it's required type.
    :param default: The default value of the input.
    """

    def __init__(self, name: str, validator=None, converter=None, default=None):
        self.name = name
        self.validator = validator
        self.converter = converter
        self.default = default

    def get(self, form: dict):
        """
        Gets the data and converts it with the converter.

        :param form: The data sent by the user.
        """

        data = form.get(self.name, self.default)

        if self.converter is not None:
            data = self.converter(data)

        return data    
        
    def validate(self, data):
        """
        Validate the data with the validator of the class.
        """
        if self.validator is None:
            return True

        if type(data) == list or type(data) == tuple:
            return self.validator.validate_many(data)
        
        return self.validator.validate(data)


class Form:
    """
    A base class for getting and validating data from forms submitted by the user.

    To add inputs to the form you can use the `inputs` attributes. To validate the data you
    can use the is_valid method. If the form is not valid, the error will be put in the error
    attribute. You can also add a model to the form that is created with the ``save`` method.
    By default the ``save`` method calls the model's create method with the arguments being the
    form data.

    :param form_data: A dictionary with all the form data from the user.
    """

    inputs = []
    model = None

    def __init__(self, form_data: dict):
        self.raw_form_data = form_data
        self.error = None

        data = {}
        for inp in self.inputs:
            try:
                data[inp.name] = inp.get(self.raw_form_data)
            except ValueError:
                self.error = f'{inp.name} is not correct type.'

        self.data = data

    def is_valid(self):
        """Checks if the form is valid."""

        # returns false if there was an error getting the data
        if self.error is not None:
            return False

        for inp in self.inputs:
            try:
                inp.validate(self.data[inp.name])
            except ValidationError as e:
                self.error = str(e)
                return False

        return True

    def save(self):
        """Creates the model in the ``model`` attribute."""
        if self.model is not None:
            return self.model.create(**self.data)
