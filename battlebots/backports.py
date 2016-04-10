import subprocess as sp


def sp_run(*popenargs, input=None, timeout=None, check=False, **kwargs):
    """Run command with arguments and return a CompletedProcess instance.

    The returned instance will have attributes args, returncode, stdout and
    stderr. By default, stdout and stderr are not captured, and those
    attributes will be None. Pass stdout=PIPE and/or stderr=PIPE in order to
    capture them.

    If check is True and the exit code was non-zero, it raises a
    CalledProcessError. The CalledProcessError object will have the return code
    in the returncode attribute, and output & stderr attributes if those
    streams were captured.

    If timeout is given, and the process takes too long, a TimeoutExpired
    exception will be raised.

    There is an optional argument "input", allowing you to
    pass a string to the subprocess's stdin.  If you use this argument
    you may not also use the Popen constructor's "stdin" argument, as
    it will be used internally.

    The other arguments are the same as for the Popen constructor.

    If universal_newlines=True is passed, the "input" argument must be a
    string and stdout/stderr in the returned object will be strings rather than
    bytes.
    """
    if input is not None:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = sp.PIPE

    with sp.Popen(*popenargs, **kwargs) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except sp.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            err = sp.TimeoutExpired(process.args, timeout, output=stdout)
            err.stderr = stderr
            raise err
        except:
            process.kill()
            process.wait()
            raise
        retcode = process.poll()
        if check and retcode:
            err = sp.CalledProcessError(retcode, process.args, output=stdout)
            err.stderr = stderr
            raise err
    return CompletedProcess(process.args, retcode, stdout, stderr)


class CompletedProcess(object):
    """A process that has finished running.

    This is returned by run().

    Attributes:
      args: The list or str args passed to run().
      returncode: The exit code of the process, negative for signals.
      stdout: The standard output (None if not captured).
      stderr: The standard error (None if not captured).
    """
    def __init__(self, args, returncode, stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        args = ['args={!r}'.format(self.args),
                'returncode={!r}'.format(self.returncode)]
        if self.stdout is not None:
            args.append('stdout={!r}'.format(self.stdout))
        if self.stderr is not None:
            args.append('stderr={!r}'.format(self.stderr))
        return "{}({})".format(type(self).__name__, ', '.join(args))
