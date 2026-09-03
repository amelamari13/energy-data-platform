from airflow.models import DagBag


def load_energy_dag():
    dag_bag = DagBag(
        dag_folder="airflow/dags"
    )
    assert dag_bag.import_errors == {}
    return dag_bag.get_dag(
        "energy_pipeline"
    )


def test_dag_imports():
    assert load_energy_dag() is not None


def test_dag_tasks():
    dag = load_energy_dag()
    assert set(dag.task_ids) == {
        "check_file",
        "run_pipeline",
        "dbt_run",
        "dbt_test",
    }


def test_dag_dependencies():
    dag = load_energy_dag()
    assert dag.get_task("check_file").downstream_task_ids == {"run_pipeline"}
    assert dag.get_task("run_pipeline").downstream_task_ids == {"dbt_run"}
    assert dag.get_task("dbt_run").downstream_task_ids == {"dbt_test"}
    assert dag.get_task("dbt_test").downstream_task_ids == set()
