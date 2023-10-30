History and Deprecations
========================

Revision History
----------------
Important changes of note with each release:

2.3.0
^^^^^
- Dropped support for Python 3.7, added support for Python 3.12
- Added History and Deprecations page to documentation.
- Added deprecation to ``create_netcdf.main``, ``create_netcdf.make_netcdf``, and ``create_netcdf.make_product_netcdf``, for closing the netCDF file after initial creation and population. As of version 2.5.0, these functions will all return an open netCDF file, or a list containing open netCDF files in the case of the function creating multiple files, e.g. multiple data products. This behaviour can be used from version 2.3.0 by passing ``return_open=True`` to these functions. As of version 2.4.0, ``return_open=True`` will be the default option, with the previous behaviour available by passing ``return_open=False``. In version 2.5.0, the behaviour of ``return_open=False`` will be removed.


Deprecation Policy
------------------
Through the life of software, it is very likely parts of the package will have to be changed and altered in such a way the user will have to make small changes to their work in order to keep up with changes in the software. While these deprecations are kept to a minimum, they cannot be altogether avoided. This policy states how this package aims to deal with changes and deprecation of code.

If something in the package is to be deprecated and replaced:

#. A ``DeprecationWarning`` must be raised when the code that will be removed will be executed, which must mention in which version of the package that thing will no longer work or be available. That version must be at least 2 minor versions later (i.e. code that raises a deprecation warning added in 2.3.x cannot be removed until 2.5.0 at the earliest).
#. If possible, a way of using the new code should be made available simultaneously. In this case, the deprecation warning must include information to the user on how to use the new code. If this is not possible, the deprecation warning should last for at least 3 minor versions (i.e. if first raised in 2.3.x, it should not be removed until 2.6.0), with beta versions of the package published with the new code.
#. If the change in the code can be contained within a boolean argument to a function, then that argument must default to the original code when the deprecation warning is first added, and removed in the version of the package where the code is deprecated, but it is allowed to change the default option to the new code in an intermediate release while the old version of the code is still available within the function. This change of default option must happen in the next minor version release at the earliest, with the code removed at least one further minor release later (i.e. if a deprecation is added in 2.3.x and is covered by a boolean argument, in 2.3.x that boolean argument must default to the original code, in 2.4.x it can default to original or new, and then the argument and original code can be removed from 2.5.0). If this default option is changed before the deprecated code is removed, this must be mentioned in the deprecation warning before the change happens (i.e. in the example above, in version 2.3.x), and in the deprecation warning afterwards (i.e. in 2.4.x) it must state how to use the original code.
#. Deprecations must be added to the documentation, including what is being deprecated, which version the deprecation warning was first introduced, in which version the original code will be removed, and all information on how to use both original and new versions of the code in the intervening releases.
#. All references to minor release versions must be superseded by a major release version, for example if a deprecation warning introduced in 2.3.x states something will be removed in 2.5.0, then that thing must be removed in 3.0.0, even if it comes out before 2.5.0 (which presumably would then not be published).
