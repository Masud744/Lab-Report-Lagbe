"""
LaTeX report generation and PDF compilation.
Uses Jinja2 templates with custom delimiters to avoid LaTeX conflicts.
Supports:
- Full academic sections (Problem Description, Methodology, Code, Visualization, Result & Discussion)
- Embedded screenshots / output images in 2x2 grid
- Dual-column code listing for long files
"""

import io
import os
import re
import base64
import zipfile
import subprocess
import tempfile
import shutil
import unicodedata
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sanitize_text(text: str) -> str:
    """Sanitize unicode quotes, dashes, symbols, emojis, and unprintable characters."""
    if not text:
        return ""
    text = str(text)

    # Common Unicode symbols and punctuation replacements
    replacements = {
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '—': '---',
        '–': '--',
        '−': '-',
        '…': '...',
        '•': '*',
        '·': '*',
        '✓': '[OK]',
        '✔': '[OK]',
        '✗': '[X]',
        '✘': '[X]',
        '★': '*',
        '☆': '*',
        '→': '->',
        '←': '<-',
        '⇒': '=>',
        '↔': '<->',
        '°': ' deg',
        '±': '+/-',
        '×': 'x',
        '÷': '/',
        '≤': '<=',
        '≥': '>=',
        '≠': '!=',
        '≈': '~',
        '©': '(C)',
        '®': '(R)',
        '™': '(TM)',
        '\r\n': '\n',
        '\r': '\n',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Filter out characters that pdflatex cannot render (emojis, unsupported non-latin scripts)
    safe_chars = []
    for ch in text:
        code = ord(ch)
        if code < 128:
            safe_chars.append(ch)
        elif 160 <= code <= 255:
            safe_chars.append(ch)
        else:
            decomp = unicodedata.normalize('NFKD', ch)
            ascii_equiv = ''.join(c for c in decomp if ord(c) < 128)
            if ascii_equiv:
                safe_chars.append(ascii_equiv)
            elif ch.isspace():
                safe_chars.append(' ')
    return "".join(safe_chars)


def _escape_latex(text: str) -> str:
    """Sanitize unicode and escape special LaTeX characters in user-supplied text."""
    if not text:
        return ""
    text = _sanitize_text(text)
    # Order matters: backslash first
    text = text.replace('\\', r'\textbackslash{}')
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def _sanitize_caption(caption: str) -> str:
    """Format caption cleanly, allowing standard math notation while protecting against unsafe commands."""
    if not caption:
        return ""
    caption = re.sub(r"^figure\s*\d+\s*:\s*", "", str(caption), flags=re.IGNORECASE).strip()
    parts = re.split(r'(\$[^$]+\$)', caption)
    safe_parts = []
    for part in parts:
        if part.startswith('$') and part.endswith('$'):
            math_expr = part[1:-1]
            math_expr = re.sub(r'\\(input|write|openout|def|let)', '', math_expr)
            safe_parts.append(f"${math_expr}$")
        else:
            safe_parts.append(_escape_latex(part))
    return "".join(safe_parts)


def _clean_code_and_output(text: str) -> str:
    """Sanitize text inside lstlisting to prevent pdflatex compilation crashes."""
    if not text:
        return ""
    text = _sanitize_text(text)

    safe_chars = []
    for char in text:
        if ord(char) < 128:
            safe_chars.append(char)
        else:
            safe_chars.append('?')
    return "".join(safe_chars)


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
    "typescript": {
        "name": "TypeScript",
        "morekeywords": "break,case,catch,continue,debugger,default,delete,do,else,finally,for,function,if,in,instanceof,new,return,switch,this,throw,try,typeof,var,void,while,with,class,const,enum,export,extends,import,super,implements,interface,let,package,private,protected,public,static,yield,async,await,of,true,false,null,undefined,console,log,type,string,number,boolean,any,never,unknown",
    },
    "go": {
        "name": "Go",
        "morekeywords": "break,case,chan,const,continue,default,defer,else,fallthrough,for,func,go,goto,if,import,interface,map,package,range,return,select,struct,switch,type,var,true,false,nil,fmt,Println,Printf",
    },
    "rust": {
        "name": "Rust",
        "morekeywords": "as,break,const,continue,crate,else,enum,extern,false,fn,for,if,impl,in,let,loop,match,mod,move,mut,pub,ref,return,self,static,struct,super,trait,true,type,unsafe,use,where,while,async,await,dyn,println,String,Vec,Option,Result",
    },
    "sql": {
        "name": "SQL",
        "morekeywords": "SELECT,FROM,WHERE,INSERT,INTO,VALUES,UPDATE,SET,DELETE,CREATE,TABLE,DROP,ALTER,JOIN,INNER,LEFT,RIGHT,OUTER,ON,GROUP,BY,ORDER,HAVING,LIMIT,AS,AND,OR,NOT,NULL,PRIMARY,KEY,FOREIGN,REFERENCES,DISTINCT,COUNT,SUM,AVG,MAX,MIN,INT,VARCHAR,TEXT,DATE,BOOLEAN",
    },
    "kotlin": {
        "name": "Kotlin",
        "morekeywords": "as,break,class,continue,do,else,false,for,fun,if,in,interface,is,null,object,package,return,super,this,throw,true,try,typealias,val,var,when,while,data,override,private,public,protected,internal,open,abstract,companion,println,print,String,Int,Double,List,Map",
    },
    "csharp": {
        "name": "C#",
        "morekeywords": "abstract,as,base,bool,break,byte,case,catch,char,checked,class,const,continue,decimal,default,delegate,do,double,else,enum,event,explicit,extern,false,finally,fixed,float,for,foreach,goto,if,implicit,in,int,interface,internal,is,lock,long,namespace,new,null,object,operator,out,override,params,private,protected,public,readonly,ref,return,sbyte,sealed,short,sizeof,stackalloc,static,string,struct,switch,this,throw,true,try,typeof,uint,ulong,unchecked,unsafe,ushort,using,virtual,void,volatile,while,var,async,await,Console,WriteLine",
    },
    "php": {
        "name": "PHP",
        "morekeywords": "abstract,and,array,as,break,callable,case,catch,class,clone,const,continue,declare,default,die,do,echo,else,elseif,empty,enddeclare,endfor,endforeach,endif,endswitch,endwhile,eval,exit,extends,final,finally,fn,for,foreach,function,global,goto,if,implements,include,instanceof,interface,isset,list,match,namespace,new,or,print,private,protected,public,readonly,require,return,static,switch,throw,trait,try,unset,use,var,while,xor,yield,true,false,null",
    },
    "ruby": {
        "name": "Ruby",
        "morekeywords": "BEGIN,END,alias,and,begin,break,case,class,def,defined,do,else,elsif,end,ensure,false,for,if,in,module,next,nil,not,or,redo,rescue,retry,return,self,super,then,true,undef,unless,until,when,while,yield,puts,print,require",
    },
    "swift": {
        "name": "Swift",
        "morekeywords": "associatedtype,class,deinit,enum,extension,fileprivate,func,import,init,inout,internal,let,open,operator,private,protocol,public,static,struct,subscript,typealias,var,break,case,continue,default,defer,do,else,fallthrough,for,guard,if,in,repeat,return,switch,where,while,as,false,is,nil,self,Self,super,throw,throws,true,try,print,String,Int,Double,Bool",
    },
    "r": {
        "name": "R",
        "morekeywords": "if,else,repeat,while,function,for,in,next,break,TRUE,FALSE,NULL,Inf,NaN,NA,library,print,cat,c,data,frame,mean,sd,sum,plot,return",
    },
    "bash": {
        "name": "Bash",
        "morekeywords": "if,then,else,elif,fi,case,esac,for,select,while,until,do,done,in,function,time,echo,printf,read,local,export,return,exit,grep,awk,sed,cat,ls,mkdir,cd,pwd",
    },
    "matlab": {
        "name": "MATLAB",
        "morekeywords": "break,case,catch,classdef,continue,else,elseif,end,for,function,global,if,otherwise,parfor,persistent,return,spmd,switch,try,while,disp,fprintf,plot,xlabel,ylabel,title,grid,zeros,ones,linspace",
    },
    "arduino": {
        "name": "Arduino (C++)",
        "morekeywords": "void,int,float,double,char,bool,byte,unsigned,long,short,const,static,if,else,for,while,do,switch,case,break,continue,return,true,false,HIGH,LOW,INPUT,OUTPUT,INPUT_PULLUP,setup,loop,pinMode,digitalWrite,digitalRead,analogRead,analogWrite,delay,Serial,begin,println,print,include",
    },
    "lua": {
        "name": "Lua",
        "morekeywords": "and,break,do,else,elseif,end,false,for,function,goto,if,in,local,nil,not,or,repeat,return,then,true,until,while,print,pairs,ipairs,table,string,math",
    },
    "perl": {
        "name": "Perl",
        "morekeywords": "my,our,local,sub,if,elsif,else,unless,while,until,for,foreach,do,next,last,redo,return,use,strict,warnings,print,say,chomp,push,pop,shift,unshift,keys,values",
    },
    "scala": {
        "name": "Scala",
        "morekeywords": "abstract,case,catch,class,def,do,else,extends,false,final,finally,for,forSome,if,implicit,import,lazy,match,new,null,object,override,package,private,protected,return,sealed,super,this,throw,trait,try,true,type,val,var,while,with,yield,println,Int,String,List,Map",
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
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )

    def generate(self, data: dict, tmpdir: str = None) -> str:
        """Generate LaTeX source from the data dict with all strings safely escaped."""
        lang = data.get("language", "python").lower()
        lang_config = LANGUAGE_LST_CONFIG.get(lang, LANGUAGE_LST_CONFIG.get("python"))

        today = datetime.now().strftime("%B %d, %Y").upper()

        safe_tasks = []
        for t_idx, task in enumerate(data.get("tasks", [])):
            # Process methodology points
            raw_methodology = task.get("methodology", [])
            safe_methodology = []
            for m in raw_methodology:
                if isinstance(m, dict):
                    safe_methodology.append({
                        "title": _escape_latex(m.get("title", "")),
                        "description": _escape_latex(m.get("description", "")),
                    })
                elif isinstance(m, str):
                    safe_methodology.append({
                        "title": f"Step {len(safe_methodology) + 1}",
                        "description": _escape_latex(m),
                    })

            # Process images/figures
            safe_images = []
            raw_images = task.get("images", [])
            for img_idx, img in enumerate(raw_images):
                img_data = img.get("data") if isinstance(img, dict) else img
                caption = img.get("caption") if isinstance(img, dict) else f"Figure {img_idx + 1}: Output"

                img_filename = f"task_{t_idx + 1}_fig_{img_idx + 1}.png"
                saved_ok = False
                if tmpdir and img_data:
                    try:
                        dest = os.path.join(tmpdir, img_filename)
                        if "base64," in img_data:
                            b64_content = img_data.split("base64,", 1)[1]
                            raw_bytes = base64.b64decode(b64_content)
                            with Image.open(io.BytesIO(raw_bytes)) as pil_img:
                                pil_img.convert("RGB").save(dest, format="PNG")
                            saved_ok = True
                        elif os.path.exists(img_data):
                            with Image.open(img_data) as pil_img:
                                pil_img.convert("RGB").save(dest, format="PNG")
                            saved_ok = True
                    except Exception as e:
                        print(f"Warning: Failed to save image {img_filename}: {e}")

                if saved_ok or not tmpdir:
                    safe_images.append({
                        "filename": img_filename,
                        "caption": _sanitize_caption(caption or f"Output state {img_idx + 1}"),
                    })


            # Check if code should be rendered in 2-column mode
            code_text = _clean_code_and_output(task.get("code", ""))
            use_multicol = len(code_text.splitlines()) > 45

            safe_tasks.append({
                "title": _escape_latex(task.get("title", "")),
                "problem_overview": _escape_latex(task.get("problem_overview") or task.get("description", "")),
                "requirements": [_escape_latex(r) for r in task.get("requirements", [])],
                "methodology": safe_methodology,
                "filename": _escape_latex(task.get("filename") or f"main.{'py' if lang == 'python' else 'dart'}"),
                "code": code_text,
                "use_multicol": use_multicol,
                "output": _clean_code_and_output(task.get("output", "")),
                "images": safe_images,
                "is_visual": task.get("is_visual", False),
                "result_discussion": _escape_latex(task.get("result_discussion") or task.get("summary", "The program executed successfully and met all specified requirements.")),
            })

        raw_title = f"{data.get('course_code', '')} - Lab {data.get('lab_number', 1)}: {data.get('lab_title', '')}"
        meta_title = "".join(c for c in _sanitize_text(raw_title) if c.isalnum() or c in " -_:.")
        meta_author = "".join(c for c in _sanitize_text(data.get("student_name", "")) if c.isalnum() or c.isspace())

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
            github_link=data.get("github_link", "").strip(),
            date_str=today,
            meta_title=meta_title,
            meta_author=meta_author,
            language_name=lang_config["name"],
            language_keywords=lang_config["morekeywords"],
            tasks=safe_tasks,
            multi_task=len(safe_tasks) > 1,
        )
        return rendered

    def compile_pdf(self, data: dict, output_filename: str) -> str:
        """Generate LaTeX and compile to PDF in a self-contained temporary directory."""
        output_dir = os.path.join(BASE_DIR, "output")
        os.makedirs(output_dir, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_content = self.generate(data, tmpdir=tmpdir)
            tex_path = os.path.join(tmpdir, "report.tex")
            with open(tex_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(tex_content)

            # Copy custom logo if provided, else default to official UFTB logo
            custom_logo = data.get("custom_logo", "")
            logo_written = False
            if custom_logo and "base64," in custom_logo:
                try:
                    raw_logo = base64.b64decode(custom_logo.split("base64,", 1)[1])
                    with Image.open(io.BytesIO(raw_logo)) as pil_logo:
                        pil_logo.save(os.path.join(tmpdir, "uftb.png"), format="PNG")
                        pil_logo.save(os.path.join(tmpdir, "logo.png"), format="PNG")
                    logo_written = True
                except Exception as e:
                    print(f"Warning: Custom logo decode failed, using default UFTB logo: {e}")

            if not logo_written:
                uftb_src = os.path.join(BASE_DIR, "static", "images", "uftb.png")
                logo_src = os.path.join(BASE_DIR, "static", "images", "logo.png")
                if os.path.exists(uftb_src):
                    shutil.copy(uftb_src, os.path.join(tmpdir, "uftb.png"))
                    shutil.copy(uftb_src, os.path.join(tmpdir, "logo.png"))
                elif os.path.exists(logo_src):
                    shutil.copy(logo_src, os.path.join(tmpdir, "logo.png"))

            # Run pdflatex twice
            last_stdout = ""
            last_stderr = ""
            for _ in range(2):
                proc = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "report.tex"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60,
                )
                last_stdout = proc.stdout.decode("utf-8", errors="replace")
                last_stderr = proc.stderr.decode("utf-8", errors="replace")

            pdf_path = os.path.join(tmpdir, "report.pdf")
            if not os.path.exists(pdf_path):
                log_path = os.path.join(tmpdir, "report.log")
                log_content = ""
                if os.path.exists(log_path):
                    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                        log_content = f.read()
                    error_lines = [
                        line for line in log_content.split("\n")
                        if line.startswith("!") or "Error" in line or "Undefined" in line
                    ]
                    if error_lines:
                        log_content = "\n".join(error_lines[:15])
                    else:
                        log_content = log_content[-1500:]
                else:
                    log_content = last_stdout[-1500:] or last_stderr[-1500:]
                raise RuntimeError(f"PDF compilation failed.\n{log_content}")

            final_path = os.path.join(output_dir, output_filename)
            shutil.copy(pdf_path, final_path)

            # Save Overleaf-ready LaTeX .zip bundle (main.tex + logo + figures)
            stem = os.path.splitext(output_filename)[0]
            zip_path = os.path.join(output_dir, f"{stem}_latex.zip")
            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.write(tex_path, arcname="main.tex")
                    for fname in os.listdir(tmpdir):
                        if fname.endswith(".png") and fname != "logo.png":
                            zf.write(os.path.join(tmpdir, fname), arcname=fname)
            except Exception as ze:
                print(f"Warning: Failed to create Overleaf zip: {ze}")

            return final_path
