#include <string>
#include <QObject>

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
    class MyClass: public QObject
    {
        Q_OBJECT
        Q_PROPERTY(double my_method READ my_method);
       public:
        MyClass();

        double my_method();
    };
}

/// This class has the same name but is a different class
class MyClass
{
   public:
    MyClass();
};
/// @}

/// A simple macro
#define MY_MACRO(x) foo(x)

// A simple enum
enum Color { red, green, blue };

// An enum class
enum class Color_c { red, green, blue };
