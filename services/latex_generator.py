import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    if not text:
        return ""
    replacements = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def _escape_code_for_latex(code: str) -> str:
    """Minimal escaping for code inside lstlisting (mostly safe as-is)."""
    return code


LANGUAGE_LST_CONFIG = {
    "dart": {
        "name": "Dart",
        "morekeywords": "abstract,as,assert,async,await,break,case,catch,class,const,continue,default,deferred,do,dynamic,else,enum,export,extends,extension,external,factory,false,final,finally,for,Function,get,hide,if,implements,import,in,interface,is,late,library,mixin,new,null,of,on,operator,part,rethrow,return,set,show,static,super,switch,sync,this,throw,true,try,typedef,var,void,while,with,yield",
    },
    "python": {
        "name": "Python",
        "morekeywords": "and,as,assert,async,await,break,class,continue,def,del,elif,else,except,False,finally,for,from,global,if,import,in,is,lambda,None,nonlocal,not,or,pass,raise,return,True,try,while,with,yield,print,self,int,str,float,list,dict,tuple,set",
    },
    "c++": {
        "name": "C++",
        "morekeywords": "auto,break,case,char,const,continue,default,do,double,else,enum,extern,float,for,goto,if,int,long,register,return,short,signed,sizeof,static,struct,switch,typedef,union,unsigned,void,volatile,while,class,namespace,template,this,new,delete,try,catch,throw,public,private,protected,virtual,friend,inline,using,bool,true,false,string,vector,map,set,cout,cin,endl,include,iostream,std",
    },
    "java": {
        "name": "Java",
        "morekeywords": "abstract,assert,boolean,break,byte,case,catch,char,class,const,continue,default,do,double,else,enum,extends,final,finally,float,for,goto,if,implements,import,instanceof,int,interface,long,native,new,package,private,protected,public,return,short,static,strictfp,super,switch,synchronized,this,throw,throws,transient,try,void,volatile,while,true,false,null,String,System",
    },
    "javascript": {
        "name": "JavaScript",
        "morekeywords": "break,case,catch,continue,debugger,default,delete,do,else,finally,for,function,if,in,instanceof,new,return,switch,this,throw,try,typeof,var,void,while,with,class,const,enum,export,extends,import,super,implements,interface,let,package,private,protected,public,static,yield,async,await,of,true,false,null,undefined,console,log",
    },
    "c": {
        "name": "C",
        "morekeywords": "auto,break,case,char,const,continue,default,do,double,else,enum,extern,float,for,goto,if,int,long,register,return,short,signed,sizeof,static,struct,switch,typedef,union,unsigned,void,volatile,while,printf,scanf,include,stdio,stdlib,string,main",
    },
}


class LaTeXGenerator:
    def __init__(self):
        template_dir = os.path.join(BASE_DIR, "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            block_start_string='<%',
            block_end_string='%>',
            variable_start_string='<<',
            variable_end_string='>>',
            comment_start_string='<#',
            comment_end_string='#>',
        )

    def generate(self, data: dict) -> str:
        """Generate LaTeX source from the data dict."""
        lang = data.get("language", "python").lower()
        lang_config = LANGUAGE_LST_CONFIG.get(lang, LANGUAGE_LST_CONFIG["python"])

        today = datetime.now().strftime("%B %d, %Y").upper()

        template = self.env.get_template("report_template.tex")
        rendered = template.render(
            student_name=_escape_latex(data.get("student_name", "")),
            student_id=_escape_latex(data.get("student_id", "")),
            session=_escape_latex(data.get("session", "")),
            university=_escape_latex(data.get("university", "University of Frontier Technology, Bangladesh")),
            university_short=_escape_latex(data.get("university_short", "UFTB")),
            department=_escape_latex(data.get("department", "Department of Internet of Things and Robotics Engineering (IRE)")),
            department_short=_escape_latex(data.get("department_short", "IRE")),
            faculty=_escape_latex(data.get("faculty", "Faculty of Cyber Physical System Engineering")),
            course_code=_escape_latex(data.get("course_code", "")),
            course_title=_escape_latex(data.get("course_title", "")),
            instructor_name=_escape_latex(data.get("instructor_name", "")),
            instructor_title=_escape_latex(data.get("instructor_title", "")),
            lab_number=data.get("lab_number", 1),
            lab_title=_escape_latex(data.get("lab_title", "")),
            lab_subtitle=_escape_latex(data.get("lab_subtitle", "")),
            github_link=data.get("github_link", ""),
            date_str=today,
            language_name=lang_config["name"],
            language_keywords=lang_config["morekeywords"],
            tasks=data.get("tasks", []),
        )
        return rendered

    def compile_pdf(self, tex_content: str, output_filename: str) -> str:
        """Compile LaTeX to PDF. Returns path to the PDF file."""
        output_dir = os.path.join(BASE_DIR, "output")
        os.makedirs(output_dir, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, "report.tex")
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            # copy logo if exists
            logo_src = os.path.join(BASE_DIR, "static", "images", "logo.png")
            if os.path.exists(logo_src):
                shutil.copy(logo_src, os.path.join(tmpdir, "logo.png"))

            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "report.tex"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

            pdf_path = os.path.join(tmpdir, "report.pdf")
            if not os.path.exists(pdf_path):
                log_path = os.path.join(tmpdir, "report.log")
                log_content = ""
                if os.path.exists(log_path):
                    with open(log_path, "r") as f:
                        log_content = f.read()[-2000:]
                raise RuntimeError(f"PDF compilation failed.\n{log_content}")

            final_path = os.path.join(output_dir, output_filename)
            shutil.copy(pdf_path, final_path)
            return final_path
