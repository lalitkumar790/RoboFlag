# Mission control

Generate real offline replay data with python -m roboflag.export_dashboard.
Serve with python -m http.server 8000 --directory dashboard and open http://localhost:8000.
The isometric canvas is a 2.5D grid renderer, not a physics simulation.
The six scenarios are a fixed exploratory replay set, not a holdout. The benchmark is separate from native Flagsmith results.
