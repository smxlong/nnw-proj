rootproject = \
'''# This file is managed by proj.

cmake_minimum_required(VERSION 3.0)

# --== proj begin rootproject ==--

# --== proj begin projectname ==--
project()
# --== proj end projectname ==--

# --== proj begin definitions ==--
# --== proj end definitions ==--

# --== proj begin subdirs ==--
# --== proj end subdirs ==--

# --== proj end rootproject ==--
'''

executable = \
'''# This file is managed by proj.

cmake_minimum_required(VERSION 3.0)

# --== proj begin executable ==--

# --== proj begin projectname ==--
project()
# --== proj end projectname ==--

# --== proj begin addexe ==--
add_executable(
# --== proj begin exename ==--
# --== proj end exename ==--

# --== proj begin sources ==--
# --== proj end sources ==--

# --== proj begin headers ==--
# --== proj end headers ==--
)
# --== proj end addexe ==--

# --== proj begin definitions ==--
# --== proj end definitions ==--

# --== proj end executable ==--
'''
