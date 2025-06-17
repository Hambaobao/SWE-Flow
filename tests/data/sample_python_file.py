"""
Sample Python file for testing.
"""

def function1():
    """
    This is function 1.
    
    Returns:
        str: A greeting message.
    """
    return "Hello from function 1"


def function2(name):
    """
    This is function 2.
    
    Args:
        name (str): The name to greet.
        
    Returns:
        str: A personalized greeting message.
    """
    return f"Hello, {name}, from function 2"


class SampleClass:
    """A sample class for testing."""
    
    def __init__(self, value):
        """
        Initialize the class.
        
        Args:
            value: The initial value.
        """
        self.value = value
    
    def method1(self):
        """
        This is method 1.
        
        Returns:
            The stored value.
        """
        return self.value
    
    @property
    def value_property(self):
        """
        A property that returns the value.
        
        Returns:
            The stored value.
        """
        return self.value
    
    @staticmethod
    def static_method():
        """
        A static method.
        
        Returns:
            str: A static message.
        """
        return "This is a static method"
