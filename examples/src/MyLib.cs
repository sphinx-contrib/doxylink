using System;
using System.Collections.Generic;

/// \defgroup ClassesGroup A group of the classes
/// @{
namespace MyCompany.MyApp
{
    /**
     * Example documented class
     */
    public class MyClass
    {
        public MyClass() { }

        /// Example documented method
        public double MyMethod() { return 0.0; }

        /// Overload taking a fully-qualified type
        public System.String MyMethod(System.String foo) { return foo; }

        /// Overload taking two fully-qualified types
        public System.String MyMethod(System.String a, System.Int32 b) { return a; }

        /// A method using a generic, fully-qualified collection type
        public void Process(System.Collections.Generic.List<System.String> items) { }

        /// A simple property
        public double MyProperty { get; set; }
    }

    /// A simple enum
    public enum Color { Red, Green, Blue }
}

/// This class has the same name but lives in a different namespace
namespace MyCompany.OtherApp
{
    public class MyClass
    {
        public MyClass() { }
    }
}
/// @}
