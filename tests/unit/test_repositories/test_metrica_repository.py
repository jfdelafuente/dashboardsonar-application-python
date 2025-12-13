"""
Unit tests for MetricaRepository.

Tests specific query methods for SonarQube metrics data.
"""

import pytest
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.models.metricas import Metrica
from infocodest.models.proveedor import Proveedor
from infocodest.extensions import db


class TestMetricaRepository:
    """Test suite for MetricaRepository query methods."""

    @pytest.fixture
    def metrica_repo(self, app):
        """Create MetricaRepository with test data."""
        with app.app_context():
            db.create_all()

            # Create sample metrics
            # Note: Due to unique constraints in model, each metrica needs unique values
            metricas = [
                Metrica(
                    repo='repo1',
                    aplicacion='App1',
                    fecha='2025-12-01',
                    bugs=10,
                    reliability_rating=1,
                    reliability_label='A',
                    vulnerabilities=2,
                    security_rating=1,
                    security_label='A',
                    code_smells=50,
                    sqale_rating=1,
                    sqale_label='A',
                    alert_status='OK',
                    project='project1',
                    complexity=100,
                    coverage=85,
                    unit_tests='100',
                    ncloc=10000,
                    duplicated_line_density=5,
                    sqale_index=500,
                    sqale_debt_ratio=10,
                    size='M',
                    dloc_label='A',
                    coverage_label='A',
                    quality_gate='Passed'
                ),
                Metrica(
                    repo='repo2',
                    aplicacion='App2',
                    fecha='2025-12-05',
                    bugs=25,
                    reliability_rating=2,
                    reliability_label='B',
                    vulnerabilities=8,
                    security_rating=2,
                    security_label='B',
                    code_smells=120,
                    sqale_rating=2,
                    sqale_label='B',
                    alert_status='ERROR',
                    project='project2',
                    complexity=200,
                    coverage=60,
                    unit_tests='80',
                    ncloc=15000,
                    duplicated_line_density=12,
                    sqale_index=1200,
                    sqale_debt_ratio=20,
                    size='L',
                    dloc_label='B',
                    coverage_label='B',
                    quality_gate='Failed'
                ),
                Metrica(
                    repo='repo3',
                    aplicacion='App1',  # Same app, different repo
                    fecha='2025-12-10',
                    bugs=5,
                    reliability_rating=3,
                    reliability_label='C',
                    vulnerabilities=0,
                    security_rating=3,
                    security_label='A',
                    code_smells=30,
                    sqale_rating=3,
                    sqale_label='A',
                    alert_status='OK',
                    project='project3',
                    complexity=150,
                    coverage=90,
                    unit_tests='120',
                    ncloc=8000,
                    duplicated_line_density=2,
                    sqale_index=300,
                    sqale_debt_ratio=5,
                    size='S',
                    dloc_label='C',
                    coverage_label='C',
                    quality_gate='Passed'
                ),
            ]

            for metrica in metricas:
                db.session.add(metrica)
            db.session.commit()

            yield MetricaRepository()

            db.session.remove()
            db.drop_all()

    def test_get_by_repo(self, metrica_repo):
        """Test retrieving metrics by repository name."""
        metrica = metrica_repo.get_by_repo('repo1')

        assert metrica is not None
        assert metrica.repo == 'repo1'
        assert metrica.aplicacion == 'App1'

    def test_get_by_repo_not_found(self, metrica_repo):
        """Test retrieving non-existent repository returns None."""
        metrica = metrica_repo.get_by_repo('nonexistent')
        assert metrica is None

    def test_get_by_aplicacion(self, metrica_repo):
        """Test retrieving all metrics for an application."""
        metricas = metrica_repo.get_by_aplicacion('App1')

        assert len(metricas) == 2  # repo1 and repo3
        assert all(m.aplicacion == 'App1' for m in metricas)
        repos = [m.repo for m in metricas]
        assert 'repo1' in repos
        assert 'repo3' in repos

    def test_get_by_aplicacion_single_result(self, metrica_repo):
        """Test retrieving metrics for application with single repo."""
        metricas = metrica_repo.get_by_aplicacion('App2')

        assert len(metricas) == 1
        assert metricas[0].aplicacion == 'App2'
        assert metricas[0].repo == 'repo2'

    def test_get_by_aplicacion_not_found(self, metrica_repo):
        """Test retrieving metrics for non-existent application."""
        metricas = metrica_repo.get_by_aplicacion('NonExistentApp')
        assert metricas == []

    def test_get_distinct_aplicaciones(self, metrica_repo):
        """Test retrieving distinct application names."""
        aplicaciones = metrica_repo.get_distinct_aplicaciones()

        assert len(aplicaciones) == 2  # App1 and App2
        assert 'App1' in aplicaciones
        assert 'App2' in aplicaciones

    def test_get_distinct_aplicaciones_no_duplicates(self, metrica_repo):
        """Test that distinct applications contain no duplicates."""
        aplicaciones = metrica_repo.get_distinct_aplicaciones()

        # App1 appears in 2 repos but should only appear once
        assert aplicaciones.count('App1') == 1
        assert aplicaciones.count('App2') == 1

    def test_base_repository_methods_work(self, metrica_repo):
        """Test that inherited BaseRepository methods work correctly."""
        # Test count
        total = metrica_repo.count()
        assert total == 3

        # Test get_all
        all_metricas = metrica_repo.get_all()
        assert len(all_metricas) == 3

        # Test exists
        exists = metrica_repo.exists(repo='repo1')
        assert exists is True

        not_exists = metrica_repo.exists(repo='nonexistent')
        assert not_exists is False

    def test_filter_by_alert_status(self, metrica_repo):
        """Test filtering metrics by alert status."""
        ok_metricas = metrica_repo.filter_by(alert_status='OK')
        assert len(ok_metricas) == 2

        error_metricas = metrica_repo.filter_by(alert_status='ERROR')
        assert len(error_metricas) == 1
        assert error_metricas[0].repo == 'repo2'

    def test_filter_by_quality_gate(self, metrica_repo):
        """Test filtering metrics by quality gate status."""
        passed = metrica_repo.filter_by(quality_gate='Passed')
        assert len(passed) == 2

        failed = metrica_repo.filter_by(quality_gate='Failed')
        assert len(failed) == 1
        assert failed[0].repo == 'repo2'

    def test_find_one_by_project(self, metrica_repo):
        """Test finding single metric by project name."""
        metrica = metrica_repo.find_one(project='project1')

        assert metrica is not None
        assert metrica.project == 'project1'
        assert metrica.repo == 'repo1'

    def test_create_new_metrica(self, metrica_repo):
        """Test creating a new metrica."""
        new_metrica = Metrica(
            repo='repo4',
            aplicacion='App3',
            fecha='2025-12-15',
            bugs=15,
            reliability_rating=4,
            reliability_label='D',
            vulnerabilities=3,
            security_rating=4,
            security_label='C',
            code_smells=75,
            sqale_rating=4,
            sqale_label='B',
            alert_status='WARN',
            project='project4',
            complexity=175,
            coverage=70,
            unit_tests='90',
            ncloc=12000,
            duplicated_line_density=8,
            sqale_index=750,
            sqale_debt_ratio=15,
            size='M',
            dloc_label='D',
            coverage_label='D',
            quality_gate='Passed'
        )

        created = metrica_repo.create(new_metrica)

        assert created.id is not None
        assert created.repo == 'repo4'
        assert created.aplicacion == 'App3'

        # Verify it was persisted
        retrieved = metrica_repo.get_by_repo('repo4')
        assert retrieved is not None
        assert retrieved.aplicacion == 'App3'

    def test_update_metrica(self, metrica_repo):
        """Test updating an existing metrica."""
        metrica = metrica_repo.get_by_repo('repo1')
        original_bugs = metrica.bugs

        metrica.bugs = 15
        metrica.alert_status = 'WARN'
        updated = metrica_repo.update(metrica)

        assert updated.bugs == 15
        assert updated.alert_status == 'WARN'
        assert updated.bugs != original_bugs

        # Verify update persisted
        retrieved = metrica_repo.get_by_repo('repo1')
        assert retrieved.bugs == 15
        assert retrieved.alert_status == 'WARN'

    def test_delete_metrica(self, metrica_repo):
        """Test deleting a metrica."""
        metrica = metrica_repo.get_by_repo('repo1')
        metrica_repo.delete(metrica)

        # Verify deletion
        retrieved = metrica_repo.get_by_repo('repo1')
        assert retrieved is None

        # Verify count decreased
        assert metrica_repo.count() == 2

    def test_paginate_metricas(self, metrica_repo):
        """Test pagination of metrics."""
        result = metrica_repo.paginate(page=1, per_page=2)

        assert len(result['items']) == 2
        assert result['total'] == 3
        assert result['page'] == 1
        assert result['per_page'] == 2
        assert result['pages'] == 2

    def test_count_by_aplicacion(self, metrica_repo):
        """Test counting metrics for specific application."""
        count_app1 = metrica_repo.count(aplicacion='App1')
        assert count_app1 == 2

        count_app2 = metrica_repo.count(aplicacion='App2')
        assert count_app2 == 1
