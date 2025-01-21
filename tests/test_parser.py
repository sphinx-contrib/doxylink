import pytest

from sphinxcontrib.doxylink import parsing

import pstats

# List of tuples of: (input, correct output)
# Input is a string, output is a tuple.
arglists = [
    ('( QUrl source )', ('', '(QUrl)')),
    ('( QUrl * source )', ('', '(QUrl*)')),
    ('( QUrl ** source )', ('', '(QUrl**)')),
    ('( QUrl ***&&** source )', ('', '(QUrl***&&**)')),
    ('( const QUrl ** source )', ('', '(const QUrl**)')),
    ('( const QUrl source )', ('', '(const QUrl)')),
    ('( QUrl & source )', ('', '(QUrl&)')),
    ('( const QUrl & source )', ('', '(const QUrl&)')),
    ('( const QUrl * source )', ('', '(const QUrl*)')),
    ('( const QUrl * const source )', ('', '(const QUrl*const)')),
    ('( const QByteArray & data, const QUrl & documentUri = QUrl() )', ('', '(const QByteArray&, const QUrl&)')),
    ('(void)', ('', '(void)')),
    ('(uint32_t uNoOfBlocksToProcess=(std::numeric_limits< uint32_t >::max)())', ('', '(uint32_t)')),
    ('( QWidget * parent = 0, const char * name = 0, Qt::WindowFlags f = 0 )', ('', '(QWidget*, const char*, Qt::WindowFlags)')),
    ('()', ('', '()')),
    ('() noexcept', ('', '()')),
    ('() const noexcept', ('', '() const')),
    ('() noexcept(true)', ('', '()')),
    ('() throw()', ('', '()')),
    ('() const throw()', ('', '() const')),
    ('() throw(false)', ('', '()')),
    ('() const &', ('', '() const&')),
    ('() &', ('', '()&')),
    ('() &&', ('', '()&&')),
    ('( int index = 0 )', ('', '(int)')),
    ('( int index = {0} )', ('', '(int)')),
    ('( bool ascending = true )', ('', '(bool)')),
    ('( const QIcon & icon, const QString & label, int width = -1 )', ('', '(const QIcon&, const QString&, int)')),
    ('( QWidget * parent = 0, const char * name = 0, Qt::WindowFlags f = Qt::WType_TopLevel )', ('', '(QWidget*, const char*, Qt::WindowFlags)')),
    ('( QMutex * mutex, unsigned long time = ULONG_MAX )', ('', '(QMutex*, unsigned long)')),
    ('(const VolumeSampler< VoxelType > &volIter)', ('', '(const VolumeSampler< VoxelType >&)')),
    ('(VolumeSampler< VoxelType > &volIter)', ('', '(VolumeSampler< VoxelType >&)')),
    ('(const VolumeSampler< VoxelType > &volIter)', ('', '(const VolumeSampler< VoxelType >&)')),
    ('(const uint32_t(&pDimensions)[noOfDims])', ('', '(const uint32_t)')),
    ('(Array< noOfDims, ElementType > &rhs)', ('', '(Array< noOfDims, ElementType >&)')),
    ('( const QString & path, const QString & nameFilter, SortFlags sort = SortFlags( Name | IgnoreCase ))', ('', '(const QString&, const QString&, SortFlags)')),
    ('( GLuint texture_id )', ('', '(GLuint)')),
    ('( Q3ValueList<T>::size_type i )', ('', '(Q3ValueList< T >::size_type)')),
    ('(STLAllocator< T, P > const *, STLAllocator< T2, P > const &)', ('', '(const STLAllocator< T, P >*, const STLAllocator< T2, P >&)')),
    ('(STLAllocator< T, P > const &, STLAllocator< T2, P > const &)', ('', '(const STLAllocator< T, P >&, const STLAllocator< T2, P >&)')),
    ('(const String &errorMessage, String logName="")', ('', '(const String&, String)')),
    ('(PixelFormat = PF_BYTE)', ('', '(PixelFormat)')),
    ('(const SharedPtr< ControllerValue< T > > &src)', ('', '(const SharedPtr< ControllerValue < T > >&)')),
    ('(typename T::iterator start, typename T::iterator last)', ('', '(typename T::iterator, typename T::iterator)')),
    ('(const Matrix4 *const *blendMatrices)', ('', '(const Matrix4*const*)')),
    ('(const Matrix4 *const *blendMatrices) const =0', ('', '(const Matrix4*const*) const')),
]

varargs = [
    ('(int nb=0,...)', ('', '(int, ...)')),
    ('printf( const char* format, ... )', ('printf', '(const char*, ...)')),
    ('fprintf( std::FILE* stream, const char* format, ... )', ('fprintf', '(std::FILE*, const char*, ...)')),
    ('sprintf( char* buffer, const char* format, ... )', ('sprintf', '(char*, const char*, ...)')),
    ('snprintf( char* buffer, std::size_t buf_size, const char* format, ... )', ('snprintf', '(char*, std::size_t, const char*, ...)')),
]

multiple_qualifiers = [
    ('(const unsigned short int &time)', ('', '(const unsigned short int&)')),
    ('(const unsigned long long int &value)', ('', '(const unsigned long long int&)')),
    ('(const int &nx, const long long *pixels=NULL)', ('', '(const int&, const long long*)')),
    ('(const int &naxis, const int *naxes, const long long *pixels=NULL)', ('', '(const int&, const int*, const long long*)')),
    ('( QReadWriteLock * readWriteLock, unsigned long time = ULONG_MAX )', ('', '(QReadWriteLock*, unsigned long)')),
]

fundamental_types = [
    ('(bool)', ('', '(bool)')),
    ('(signed char)', ('', '(signed char)')),
    ('(unsigned char)', ('', '(unsigned char)')),
    ('(short)', ('', '(short)')),
    ('(short int)', ('', '(short int)')),
    ('(signed short)', ('', '(signed short)')),
    ('(signed short int)', ('', '(signed short int)')),
    ('(unsigned short)', ('', '(unsigned short)')),
    ('(unsigned short int)', ('', '(unsigned short int)')),
    ('(int)', ('', '(int)')),
    ('(signed)', ('', '(signed)')),
    ('(signed int)', ('', '(signed int)')),
    ('(unsigned)', ('', '(unsigned)')),
    ('(unsigned int)', ('', '(unsigned int)')),
    ('(long)', ('', '(long)')),
    ('(long int)', ('', '(long int)')),
    ('(signed long)', ('', '(signed long)')),
    ('(signed long int)', ('', '(signed long int)')),
    ('(unsigned long)', ('', '(unsigned long)')),
    ('(unsigned long int)', ('', '(unsigned long int)')),
    ('(long long)', ('', '(long long)')),
    ('(long long int)', ('', '(long long int)')),
    ('(signed long long)', ('', '(signed long long)')),
    ('(signed long long int)', ('', '(signed long long int)')),
    ('(unsigned long long)', ('', '(unsigned long long)')),
    ('(unsigned long long int)', ('', '(unsigned long long int)')),
    ('(float)', ('', '(float)')),
    ('(double)', ('', '(double)')),
    ('(long double)', ('', '(long double)')),
]

numbers_for_defaults = [
    ('( const QPixmap & pixmap, const QString & text, int index = -1 )', ('', '(const QPixmap&, const QString&, int)')),
    ('( const char ** strings, int numStrings = -1, int index = -1 )', ('', '(const char**, int, int)')),
    ('( const QStringList & list, int index = -1 )', ('', '(const QStringList&, int)')),
]

flags_in_defaults = [
    ('( const QString & text, int column, ComparisonFlags compare = ExactMatch | Qt::CaseSensitive )', ('', '(const QString&, int, ComparisonFlags)')),
]

functions = [
    ('PolyVox::Volume::getDepth', ('PolyVox::Volume::getDepth', '')),
    ('PolyVox::Volume::getDepth()', ('PolyVox::Volume::getDepth', '()')),
    ('Volume::getVoxelAt(uint16_t uXPos, uint16_t uYPos, uint16_t uZPos, VoxelType tDefault=VoxelType()) const', ('Volume::getVoxelAt', '(uint16_t, uint16_t, uint16_t, VoxelType) const')),
    ('PolyVox::Array::operator[]', ('PolyVox::Array::operator[]', '')),
    ('operator[]', ('operator[]', '')),
    ('MyClass::operator()', ('MyClass::operator()', '')),
    ('operator()', ('operator()', '')),
]

multiple_namespaces = [
    ('PolyVox::Test::TestFunction(int foo)', ('PolyVox::Test::TestFunction', '(int)')),
]

keywords_almost_in_typenames = [
    ('evolve(quantumdata::StateVector &, const structure::QuantumSystem &, const evolution::Pars &)', ('evolve', '(quantumdata::StateVector&, const structure::QuantumSystem&, const evolution::Pars&)')),
]


@pytest.mark.parametrize('test_input, expected', functions)
def test_split_function(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', arglists)
def test_normalise_arglist(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', varargs)
def test_varargs(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', multiple_qualifiers)
def test_multiple_qualifiers(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', fundamental_types)
def test_fundamental_types(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', numbers_for_defaults)
def test_numbers_for_defaults(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', flags_in_defaults)
def test_flags_in_defaults(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', multiple_namespaces)
def test_multiple_namespaces(test_input, expected):
    assert parsing.normalise(test_input) == expected


@pytest.mark.parametrize('test_input, expected', keywords_almost_in_typenames)
def test_keywords_almost_in_typenames(test_input, expected):
    assert parsing.normalise(test_input) == expected


def test_false_signatures():
    # This is an invalid function definition. Caused by a bug in Doxygen. See openbabel/src/ops.cpp : theOpCenter("center")
    from pyparsing import ParseException
    with pytest.raises(ParseException):
        parsing.normalise('("center")')


if __name__ == "__main__":
    try:
        import cProfile as profile
    except ImportError:
        import profile

    all_tests = arglists + varargs + multiple_qualifiers + functions + numbers_for_defaults + flags_in_defaults
    all_tests += all_tests + all_tests + all_tests + all_tests

    profile.runctx("for arglist in all_tests: parsing.normalise(arglist[0])", globals(), locals(), filename='parsing_profile')
    p = pstats.Stats('parsing_profile')
    p.strip_dirs().sort_stats('time', 'cumtime').print_stats(40)
