import psycopg2
from odoo import http, fields
from odoo.http import request
import logging
import re

_logger = logging.getLogger(__name__)

class DatabaseMonitoring(http.Controller):

    @http.route('/db/monitoring/general/status', type='json', auth='user')
    def get_general_status(self):
        """Récupère des informations générales sur la base de données."""
        try:
            # Connexion à la base de données courante
            db_name = request.env.cr.dbname
            # Requête combinée pour récupérer toutes les informations, avec les connexions actives et les verrous en attente
            query = """
            SELECT
                (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public') AS table_count,
                pg_database_size(current_database()) AS db_size,
                (SELECT COUNT(*) FROM pg_class WHERE relkind IN ('v', 'm') AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) AS view_count,
                (SELECT version()) AS postgres_version,
                (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active') AS active_connections,
                (SELECT COUNT(*) FROM pg_locks WHERE granted = 'f') AS pending_locks
            """
            request.env.cr.execute(query)
            result = request.env.cr.fetchone()
            if result:
                # Extraction des données
                table_count, db_size, view_count, postgres_version_raw, active_connections, pending_locks = result
                postgres_version = "N/A"
                # Extraire la version de PostgreSQL
                if postgres_version_raw:
                    match = re.search(r"PostgreSQL (\d+\.\d+)", postgres_version_raw)
                    if match:
                        postgres_version = match.group(1)
                # Retourner les résultats formatés
                data = {
                    'table_count': table_count,
                    'db_size': round(db_size / (1024 ** 2), 2),  # Convertir en Mo
                    'postgres_version': postgres_version,
                    'view_count': view_count,
                    'active_connections': active_connections,
                    'pending_locks': pending_locks,
                }

              
                return data
            else:
                return {'error': 'Impossible de récupérer les informations'}
        
        except Exception as e:
            _logger.error(f"Erreur lors de la récupération du statut général : {e}")
            return {'error': str(e)}


   
    @http.route('/db/monitoring/query/statistics', type='json', auth='user')
    def get_query_statistics(self):
        """Récupère des statistiques sur les requêtes exécutées."""
        try:
            query = """
                SELECT 
                    sum(xact_commit) as total_commits,
                    sum(xact_rollback) as total_rollbacks,
                    sum(tup_returned) as total_rows_read,
                    sum(tup_inserted + tup_updated + tup_deleted) as total_rows_modified,
                    sum(blks_read + blks_hit) as total_blocks_accessed
                FROM 
                    pg_stat_database;
            """
            request.env.cr.execute(query)
            result = request.env.cr.fetchone()
            return {
                'total_commits': result[0],
                'total_rollbacks': result[1],
                'total_rows_read': result[2],
                'total_rows_modified': result[3],
                'total_blocks_accessed': result[4],
            }
        except Exception as e:
            _logger.error(f"Erreur lors de la récupération des statistiques des requêtes : {e}")
            return {'error': str(e)}

   
    @http.route('/db/monitoring/query/tuples/in', type='json', auth='user')
    def get_tuples_in(self):
        try:
            # Requête SQL pour obtenir les statistiques de la base de données
            query = """
                SELECT
                    SUM(n_tup_ins) AS inserts,
                    SUM(n_tup_upd) AS updates,
                    SUM(n_tup_del) AS deletes
                FROM pg_stat_user_tables
            """
            # Exécution de la requête
            request.env.cr.execute(query)
            result = request.env.cr.fetchone()

            # Si result est None, les données ne sont pas récupérées, alors renvoyer des valeurs par défaut
            if result is None:
                return {'inserts': 0, 'updates': 0, 'deletes': 0}


            # Renvoyer les données au frontend
            return {
                'inserts': result[0] or 0,
                'updates': result[1] or 0,
                'deletes': result[2] or 0
            }

        except Exception as e:
            # En cas d'erreur, loguer l'erreur et renvoyer des valeurs par défaut
            _logger.error(f"Erreur lors de la récupération des statistiques de la base de données: {str(e)}")
            return {'inserts': 0, 'updates': 0, 'deletes': 0}

    @http.route('/db/monitoring/query/tuples/out', type='json', auth='user')
    def get_tuples_out(self):
        try:
            # Requête SQL pour obtenir les statistiques des lignes récupérées via index et séquentielles
            query = """
                SELECT
                    SUM(idx_tup_fetch) AS fetched,  -- Lignes récupérées via index
                    SUM(seq_tup_read) AS returned   -- Lignes lues via scans séquentiels
                FROM pg_stat_all_tables
            """
            # Exécution de la requête
            request.env.cr.execute(query)
            result = request.env.cr.fetchone()

            # Si result est None, les données ne sont pas récupérées, alors renvoyer des valeurs par défaut
            if result is None:
                _logger.warning("Aucune donnée récupérée pour les statistiques des lignes récupérées et retournées.")
                return {'fetched': 0, 'returned': 0}
            # Renvoyer les données au frontend
            return {
                'fetched': result[0] or 0,
                'returned': result[1] or 0
            }

        except Exception as e:
            # En cas d'erreur, loguer l'erreur et renvoyer des valeurs par défaut
            _logger.error(f"Erreur lors de la récupération des statistiques des lignes récupérées et retournées: {str(e)}")
            return {'fetched': 0, 'returned': 0}


    @http.route('/db/monitoring/query/block/io', type='json', auth='user')
    def get_block_io(self):
        query = """
           SELECT
            SUM(blks_read) AS reads,      -- Total des blocs lus
            SUM(blks_hit) AS hits         -- Total des blocs trouvés dans le cache
        FROM pg_stat_database
        """
        request.env.cr.execute(query)
        result = request.env.cr.fetchone()
        return {
            'reads': result[0] or 0,  # Renvoie les blocs lus, ou 0 si aucun résultat
            'hits': result[1] or 0     # Renvoie les hits, ou 0 si aucun résultat
        }




    @http.route('/db/monitoring/table/sizes', type='json', auth='user')
    def get_table_sizes(self):
        """Récupère la taille des tables principales, triées de la plus grande à la plus petite."""
        try:
            query = """
                SELECT 
                    relname AS table_name,
                    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
                    pg_total_relation_size(relid) AS total_size_bytes
                FROM 
                    pg_catalog.pg_statio_user_tables 
                ORDER BY 
                    pg_total_relation_size(relid) DESC  -- Trie de la plus grande taille à la plus petite
                LIMIT 10;  -- Limite à 10 tables pour éviter des résultats trop volumineux
            """
            request.env.cr.execute(query)
            results = request.env.cr.fetchall()
            table_sizes = [[row[0],row[1]] for row in results]
            return table_sizes
        except Exception as e:
            _logger.error(f"Erreur lors de la récupération des tailles des tables : {e}")
            return {'error': str(e)}




  