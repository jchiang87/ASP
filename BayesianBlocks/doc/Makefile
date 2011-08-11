all:
	cat ${GLASTPOLICYROOT}/doc/Doxyfile Doxyfile > Doxyfile.tmp
	doxygen Doxyfile.tmp
	rm -f Doxyfile.tmp
	cp doxy-html/* /u/gl/jchiang/public_html/BB_docs/
