This is a script to add svg color glyphs to a font.

## Requirement
- ttx (in AFDKO)
  - Install from [Adobe site](http://www.adobe.com/devnet/opentype/afdko.html).
- lxml
  - `$ pip install lxml`

## Usage
```sh
$ ttx -x NAME -x "SVG " -o source.ttx source.otf
$ vim generate.py # edit some config
$ python generate.py
$ ttx -o out.otf out.ttx
```

If you add `nyan.svg` to the font, you can display the glyph when you type `:nyan:`.



## LICENSE
`source.otf` (Adobe Source Code Pro) is licensed under SIL OPEN FONT LICENSE Version 1.1.

Other files are licensed under MIT Lisence.
