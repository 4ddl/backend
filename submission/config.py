from ddlcw import languages
from ddlcw import config


class Language:
    C = 'c'
    CPP = 'cpp'
    JAVA = 'java'
    PYTHON = 'python'
    GO = 'go'
    LANGUAGE_CONFIG = {
        C: languages.c_lang_config,
        CPP: languages.cpp_lang_config,
        PYTHON: languages.py3_lang_config,
        GO: languages.go_lang_config,
        JAVA: languages.java_lang_config
    }
    LANGUAGE_CHOICES = (
        (C, "C (GCC 9.3.0)"),
        (CPP, "C++ (G++ 9.3.0)"),
        (JAVA, "Java (OpenJDK 14.0.1)"),
        (PYTHON, "Python (Python 3.8.2)"),
        (GO, 'Go (Golang 1.13.8)')
    )


class Verdict:
    PENDING = 'P'
    RUNNING = 'R'
    ACCEPTED = 'AC'
    PRESENTATION_ERROR = 'PE'
    TIME_LIMIT_EXCEEDED = 'TLE'
    MEMORY_LIMIT_EXCEEDED = 'MLE'
    WRONG_ANSWER = 'WA'
    RUNTIME_ERROR = 'RE'
    OUTPUT_LIMIT_EXCEEDED = 'OLE'
    COMPILE_ERROR = 'CE'
    SYSTEM_ERROR = 'SE'
    VERDICT_DICT = {
        config.RESULT_SUCCESS: ACCEPTED,
        config.RESULT_CPU_TIME_LIMIT_EXCEEDED: TIME_LIMIT_EXCEEDED,
        config.RESULT_MEMORY_LIMIT_EXCEEDED: MEMORY_LIMIT_EXCEEDED,
        config.RESULT_PRESENTATION_ERROR: PRESENTATION_ERROR,
        config.RESULT_REAL_TIME_LIMIT_EXCEEDED: TIME_LIMIT_EXCEEDED,
        config.RESULT_RUNTIME_ERROR: RUNTIME_ERROR,
        config.RESULT_SYSTEM_ERROR: SYSTEM_ERROR,
        config.RESULT_WRONG_ANSWER: WRONG_ANSWER
    }
    VERDICT_CHOICES = (
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (ACCEPTED, 'Accepted'),
        (PRESENTATION_ERROR, 'Presentation Error'),
        (TIME_LIMIT_EXCEEDED, 'Time Limit Exceeded'),
        (MEMORY_LIMIT_EXCEEDED, 'Memory Limit Exceeded'),
        (WRONG_ANSWER, 'Wrong Answer'),
        (RUNTIME_ERROR, 'Runtime Error'),
        (OUTPUT_LIMIT_EXCEEDED, 'Output Limit Exceeded'),
        (COMPILE_ERROR, 'Compile Error'),
        (SYSTEM_ERROR, 'System Error'),
    )
