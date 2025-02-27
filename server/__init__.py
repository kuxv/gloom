import scenarios
import solver

from flask import Flask, url_for, jsonify, redirect, request, render_template, abort
import time
app = Flask( __name__, static_folder='../static/dist', template_folder='../static' )
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Configuration
from production import production
debug = not production

title = 'Gloomhaven Monster Mover'
version_major = 2
version_minor = 7
version_build = 1
version = str( version_major ) + '.' + str( version_minor ) + '.' + str( version_build )
client_local_storage_version_major = 1
client_local_storage_version_minor = 3
client_local_storage_version_build = 0
client_local_storage_version = str( client_local_storage_version_major ) + '.' + str( client_local_storage_version_minor ) + '.' + str( client_local_storage_version_build )

# Routes

@app.route( '/' )
@app.route( '/<scenario>' )
def root( scenario='' ):
  return templates( 'index.html' )

@app.route( '/los' )
@app.route( '/los/<scenario>' )
def los( scenario='' ):
  return templates( 'index.html', params={
    'los_mode': True,
  } )

@app.route( '/templates/<filename>' )
def templates( filename, params={} ):
  template_version = version
  if debug:
    template_version += '.' + str( time.time() )

  return render_template(
    filename,
    debug_server=debug,
    title=title,
    version=template_version,
    client_local_storage_version=client_local_storage_version,
    client_local_storage_version_major=client_local_storage_version_major,
    client_local_storage_version_minor=client_local_storage_version_minor,
    client_local_storage_version_build=client_local_storage_version_build,
    **params
  )

@app.route( '/solve', methods=[ 'PUT' ] )
def solve():
  packed_scenario = request.json
  # if not production:
  #   print packed_scenario

  # todo: validate packed scenario format
  map_width = packed_scenario['width']
  map_height = packed_scenario['height']
  scenario_id = packed_scenario['scenario_id']
  solve_view = packed_scenario['solve_view']

  s = solver.Scenario()
  if not production:
    s.logging = True
    s.debug_visuals = True
  scenarios.init( s, map_width, map_height, 7, 7 )
  s.unpack_scenario( packed_scenario )
  actions, reach, sight = s.solve( solve_view > 0, solve_view > 1 )

  solution = {
    'scenario_id': scenario_id,
    'actions': actions,
  }
  if reach:
    solution['reach'] = reach
  if sight:
    solution['sight'] = sight

  # if not production:
  #   print solution
  return jsonify( solution )

@app.route( '/views', methods=[ 'PUT' ] )
def views():
  packed_scenario = request.json
  # if not production:
  #   print packed_scenario

  # todo: validate packed scenario format
  map_width = packed_scenario['width']
  map_height = packed_scenario['height']
  scenario_id = packed_scenario['scenario_id']
  viewpoints = packed_scenario['viewpoints']
  solve_view = packed_scenario['solve_view']

  s = solver.Scenario()
  if not production:
    s.logging = True
    s.debug_visuals = True
  scenarios.init( s, map_width, map_height, 7, 7 )
  s.unpack_scenario_forviews( packed_scenario )

  solution = {
    'scenario_id': scenario_id,
  }
  if solve_view > 0:
    solution['reach'] = s.solve_reaches( viewpoints )
  if solve_view > 1:
    solution['sight'] = s.solve_sights( viewpoints )

  # if not production:
    # print solution
  return jsonify( solution )

@app.route( '/spoilers', methods=[ 'PUT' ] )
def spoilers():
  packed_scenario = request.json
  # if not production:
  #   print packed_scenario

  # todo: validate packed scenario format
  map_width = packed_scenario['width']
  map_height = packed_scenario['height']
  spoilers_scenario_id = packed_scenario['spoilers_scenario_id']

  s = solver.Scenario()
  if not production:
    s.logging = True
    s.debug_visuals = True
  scenarios.init( s, map_width, map_height, 7, 7 )
  s.unpack_scenario_for_spoilers( packed_scenario )

  solution = {
    'spoilers_scenario_id': spoilers_scenario_id,
  }
  solution['spoilers'] = s.solve_spoilers()

  # if not production:
    # print solution
  return jsonify( solution )

# Debug Server
if __name__ == '__main__':
  import os

  if not production:
    if os.environ.get( 'WERKZEUG_RUN_MAIN' ) != 'true':
      failures = solver.perform_unit_tests( 1 )
      if failures > 0:
        exit()

  extra_files = []
  if not production:
    template_diretory = '../static'
    for _, _, files in os.walk( template_diretory ):
      for file in files:
        file = os.path.join( template_diretory, file )
        extra_files.append( file )
    template_diretory = '../static/dist'
    for _, _, files in os.walk( template_diretory ):
      for file in files:
        file = os.path.join( template_diretory, file )
        extra_files.append( file )

  app.run( debug=debug, extra_files=extra_files )