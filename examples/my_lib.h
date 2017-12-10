#include <string>

/**
 * Example documented function
 */
int my_func();

int my_func(int foo);

int my_func(float);

int my_func(std::string a, int b);

int my_func(int b, std::string a);


/// \defgroup ClassesGroup A group of the classes
/// @{
namespace my_namespace
{
    class MyClass
    {
        MyClass();
    };
}

/// This class has the same name but is a different class
class MyClass
{
    MyClass();
};
/// @}

/// A simple macro
#define MY_MACRO(x) foo(x)
