from fasthtml.common import * # pyright: ignore
from html.parser import HTMLParser
from dataclasses import dataclass, field
import subprocess
import os

TAGS_WITHOUT_ENDS = [ "img", "input", "br", "hr", "meta", "link", "base", "col", "area", "param" ]
PYTHON_KWS = [
        "False", "None", "True", "and", "as", "assert", "async", "await", "break",
        "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global",
        "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
        "try", "while", "with", "yield"
        ]
# Tags that need to be done through ft_hx
MANUAL_TAGS = ["path"]

AUTO_FORMATTER = os.environ.get("AUTO_FORMATTER", "ruff format")
PATH_TO_FILE = os.environ.get("PATH_TO_FILE", os.path.join("out", "fasthtml.py"))
AUTO_FORMATTER_CMD = os.environ.get("AUTO_FORMATTER_CMD", f"{AUTO_FORMATTER} {PATH_TO_FILE}")

app,rt = fast_app()

@dataclass
class Node:
    tag: str
    parent: "None | Node"
    attrs: list[tuple[str, str | None]]
    children: list["Node"] = field(default_factory=list)
    data: str | None = None

class FastHtmlParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if there are more than one children of this starting
        #   node they will be put in the the tuple syntax
        special_tuple = Node(tag="", attrs=[], parent=None)
        self.head = special_tuple
        self.current = special_tuple
        self.fast_html_string = ""

    def handle_starttag(self, tag, attrs):
        new_node = Node(tag=tag, attrs=attrs, parent=self.current)
        self.current.children.append(new_node)
        if tag not in TAGS_WITHOUT_ENDS:
            self.current = new_node
            

    def handle_endtag(self, tag): # pyright: ignore
        if self.current.parent is not None and (tag not in TAGS_WITHOUT_ENDS):
            self.current = self.current.parent

    def handle_data(self, data):
        data = data.strip()
        data = None if data == "" else data
        self.current.data = data

    def generate_fast_html(self) -> None:
        if len(self.head.children) > 1:
            self.fast_html_string += "(" # )
            for child in self.head.children:
                self.add_node_to_string(child)
                self.fast_html_string += ","
            self.fast_html_string += ")"
        elif len(self.head.children) == 1:
            self.add_node_to_string(self.head.children[0])


    def add_node_to_string(self, node: Node) -> None:
        py_attr_vals: list[tuple[str, str | None]] = []
        # tag
        if node.tag in MANUAL_TAGS:
            self.fast_html_string += f'ft_hx("{node.tag}"' # )
            if node.data is not None or node.children or node.attrs:
                self.fast_html_string += ","
        else:
            self.fast_html_string += node.tag.capitalize().replace("-", "_") + "(" # )
        # data
        if node.data is not None:
            self.fast_html_string += f'"{node.data}"'
            if node.children or node.attrs:
                self.fast_html_string += ","
        # other nodes
        for i, child in enumerate(node.children):
            self.add_node_to_string(child)
            last_child = i == len(node.children) - 1
            if not (last_child and len(node.attrs) == 0):
                self.fast_html_string += ", "
        # attributes
        for attr_name, attr_value in node.attrs:
            if attr_name == "class":
                py_attr = "cls"
            elif attr_name == "type":
                py_attr = "inputmode"
            else:
                py_attr = attr_name.replace("-", "_")
                if py_attr in PYTHON_KWS:
                    py_attr = "_" + py_attr
            if attr_value is None:
                py_attr_vals.append((py_attr, attr_value))
                continue
            single_quotes = "'" in attr_value
            double_quotes = '"' in attr_value
            if single_quotes and double_quotes:
                if attr_value[-1] == "'":
                    # in the case where the last character is ' it needs to be escaped
                    modified_string = attr_value[:-1] + "\\" + attr_value[-1]
                py_value = f"'''{attr_value}'''"
            elif double_quotes:
                py_value = f"'{attr_value}'"
            else:
                py_value = f'"{attr_value}"'

            py_attr_vals.append((py_attr, py_value))
        py_attr_sequence = ",".join([f'{py_attr}=None' if py_val is None else f'{py_attr}={py_val}' 
                                      for py_attr, py_val in py_attr_vals])
        self.fast_html_string += py_attr_sequence
        # end tag
        self.fast_html_string += ")"

copy_fast_html = '''
    function copyHtml() {
        let textarea = document.getElementById('html_text');
        textarea.select();
        textarea.setSelectionRange(0, 99999); // For mobile devices
        document.execCommand('copy');
        textarea.setSelectionRange(0, 0);
    }
'''
copy_icon = Svg(
        ft_hx(
            "path",
            d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1z",
            ),
        ft_hx(
            "path",
            d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0z",
            ),
        onclick="copyHtml()",
        hx_get="/copyIcon/copied",
        hx_swap="outerHTML",
        hx_target="this",
        style="cursor: pointer; display: inline",
        xmlns="http://www.w3.org/2000/svg",
        width="64",
        height="64",
        fill="currentColor",
        cls="bi bi-clipboard",
        viewbox="0 0 16 16",
        )
copied_icon = Svg(
        ft_hx(
            "path",
            fill_rule="evenodd",
            d="M10.854 7.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7.5 9.793l2.646-2.647a.5.5 0 0 1 .708 0",
            ),
        ft_hx(
            "path",
            d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1z",
            ),
        ft_hx(
            "path",
            d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0z",
            ),
        xmlns="http://www.w3.org/2000/svg",
        hx_trigger="load delay:500ms",
        color="green",
        hx_swap="outerHTML",
        hx_target="this",
        hx_get="/copyIcon/copy",
        width="64",
        height="64",
        fill="currentColor",
        cls="bi bi-clipboard-check",
        viewbox="0 0 16 16",
        )

@rt('/copyIcon/{copy_or_copied}')
def get(copy_or_copied: str): # pyright: ignore
    return copied_icon if copy_or_copied == "copied" else copy_icon

@rt('/')
def get(): 
    return (
            Title("Html2FastHtml"), 
            Br(),
            Div(
                Form(
                    Textarea(id="html_text", rows="20"),
                    Button("To FastHtml", _type="submit"),
                    copy_icon,
                    Label("Automatic Copy to Clipboard", _for="automaticCopy", style="display: inline"),
                    Input(id="automatic_copy", _type="checkbox"),
                    hx_target="#html_text",
                    hx_swap="outerHTML",
                    hx_post="/toFastHtml",
                    ),
                style="position: relative",
                cls="container",
                ),
            Script(copy_fast_html)
            )

@dataclass
class ToFastHtmlRequest:
    html_text: str
    automatic_copy: bool = False

@rt('/toFastHtml')
def post(fast_html_body: ToFastHtmlRequest): 
    html_parser = FastHtmlParser()
    html_parser.feed(fast_html_body.html_text)
    html_parser.generate_fast_html()

    with open(PATH_TO_FILE, "w") as file:
        file.write(html_parser.fast_html_string)
    subprocess.run(AUTO_FORMATTER_CMD, shell=True)
    with open(PATH_TO_FILE, "r") as file:
        fast_html_text = file.read()
    script_contents = "copyHtml()" if fast_html_body.automatic_copy else ""
    return Textarea(
            fast_html_text,
            id="html_text",
            rows="20"), Script(script_contents)

serve()
