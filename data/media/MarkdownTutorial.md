#A h1 header

Paragraphs are separated by a blank line.

2nd paragraph. *Italic*, **bold**, ***both*** and `monospace`. 


Here is a bullet list:

- apple
	- green apple
	- red apple
- banana
- orange

Here is a numbered list:

1. apple
	1. green apple
	2. red apple
2. banana
3. orange

> Block quotes are written like so.
> They can span multiple paragraphs, if you like.

>> You can also have a nested block quote



## A h2 header

To write code, you indent it by 4 spaces or a tab. Remarkable will guess what language you are writing

	def main():
		print "Hello World"
  

You can also use delimited blocks like so

~~~
public class Markdown {
	public static void main(String [] args) {
		System.out.println("Markdown is simple!");
	}
}
~~~

You can specifiy which programming language you are using with delimited blocks if you wish

~~~c
#include <stdio.h>
int main()
{
   printf("Remarkable markdown editor");
   return 0;
}
~~~

### A h3 header ###

Here is a link to the Remarkable website
 [Remarkable](http://remarkableapp.github.io)


Remarkable will also auto-detect links, e.g: google.com

Here is how to specify an image
![Alt text](https://remarkableapp.github.io/images/remarkable.png)


A horizontal rule is as follows:

---

~~Strikethrough text~~

==Highlight text==

Some text ~Subscript~

Some text ^Superscript^

---

You can specify an inline MathJax equation like so $x^2+y^2=z^2$

Or a block level equation with two dollar signs on both sides of the equation:
$$\sum_{i=0}^n i^2 = \frac{(n^2+n)(2n+1)}{6}$$


Here's a "line block":

| Line one
|   Line too
| Line tree

---

### Notes about Remarkable

With Remarkable you export your files to HTML or PDF through the `File` menu. You can also copy the converted Markdown to HTML to the clipboard through the `Edit` menu (Copy to HTML; Copy Selection to HTML).

You can swap the position of the editor and live preview pane, switch you a horizontal layout and even hide the live preview pane completely. (See `View` menu).

You can preview how the document will be rendered in your default browser by clicking `View->Preview Externally`.

You can switch to a "Night Mode" by clicking `View->Night Mode`. Note that only some Gtk themes support this, it depends on which theme you are currently using.

You can click on links in the live preview pane to verify them. To return to the markdown document just edit the file (e.g. make a space and then delete it).

Check out the [Remarkable Website Here](http://remarkableapp.github.io) and the [GithHub repository](http://github.com/jamiemcg/remarkable).