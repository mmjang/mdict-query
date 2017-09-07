This is a python module for looking up `mdict` dictionary files (`.mdx` and `.mdd`). Function converting `mdx` to `sqlite` is added.

>>Based on [readmdict](https://bitbucket.org/xwang/mdict-analysis) by [Xiaoqiang Wang](http://bitbucket.org/xwang/).

While this project is a trivial extension of the [original module](https://bitbucket.org/xwang/mdict-analysis), it adds the features of looking up a single entry in `.mdx` or resource file in `.mdd` without extracting all content, which may be helpful in other projects that requires dictionaries.

## Usage

Constructs the `IndexBuilder` object, which builds the sqlite index for `.mdx` file and the corresponding `.mdd` file (if exists).

    from mdict_query import IndexBuilder
    builder = IndexBuilder('ode.mdx')

Convert `mdx` to `sqlite`:  
```
builder.make_sqlite()
# Check the output file `ode.mdx.sqlite.db` near your `ode.mdx`
```


Get all mdx keys:

    builder.get_mdx_keys()
    # ==> ['key1', 'key2', 'key3', ...]

Filter mdx keys by wildcard:

    builder.get_mdx_keys('dedicat*')
    # ==> ['dedicate', 'dedication', ...]

Looks up mdx with a key:

    result_text = builder.mdx_lookup('dedication')

There is an option to ignore cases:

    result_text = builder.mdx_lookup('Dedication', ignorecase = True)
    
Get all mdd keys:

    builder.get_mdd_keys()
    # ==> ['key1', 'key2', 'key3', ...]

Filter mdd keys by wildcard:

    builder.get_mdd_keys('*.css')
    # ==> ['/style.css', ...]
    
Looks up mdd with a key:

    bytes_list = builder.mdd_lookup('/style.css')
    #bytes_list is the bytes list of the file stored in mdd

