# Browser SDK excluded

The original generated browser SDK and its source map are not included in this
backend-only evaluation package. They contain upstream author contact details.
The files at the existing paths are import-compatible placeholders, not a working
browser SDK. Browser event capture through these static endpoints is out of scope.
Backend event APIs, analytics code and their tests are unchanged.
Restore the correctly licensed upstream SDK separately before using browser capture.
