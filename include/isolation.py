import inspect
import logging
from typing import Dict, Any, Type
from airflow.models import BaseOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator


def assemble_command(operator, *args, **kwargs):
    """Turn an Operator and it's args and/or kwargs into something that can be run directly in a Python shell
    >>> assemble_command(BaseOperator, task_id="foo")
    "from airflow.models.baseoperator import BaseOperator; BaseOperator(task_id='foo').execute({})"
    """
    _args = ', '.join(args)
    _kwargs = ', '.join(f"{k}={repr(v)}" for k, v in kwargs.items())
    if _args and _kwargs:
        _cmd = f"{_args}, {_kwargs}"
    elif _args or _kwargs:
        _cmd = f"{_args}{_kwargs}"
    else:
        _cmd = ""
    import_path = f"from {inspect.getmodule(operator).__name__} import {operator.__name__}; "
    operator = f"""{operator.__name__}({_cmd})"""
    execute = ".execute({})"
    return import_path + operator + execute


class IsolatedOperator(KubernetesPodOperator):
    # TODO - ExternalPython as well
    isolated_operator_args = ["task_id", "image", "cmds", "arguments"]

    def __init__(
            self,
            image: str,
            operator: Type[BaseOperator],
            task_id: str,
            kubernetes_pod_operator_kwargs: Dict[str, Any],
            *args,
            **kwargs
    ):
        for k in IsolatedOperator.isolated_operator_args:
            if k in kubernetes_pod_operator_kwargs:
                logging.warning(
                    "The following cannot be set in 'kubernetes_pod_operator_kwargs' "
                    "and must be set in IsolatedOperator (task_id, image) or left unset (cmds, arguments)"
                )
                del kubernetes_pod_operator_kwargs[k]
        super().__init__(
            task_id=task_id,
            image=image,
            cmds=["python"],
            arguments=["-c", assemble_command(operator, *args, **kwargs)],
            **kubernetes_pod_operator_kwargs
        )
