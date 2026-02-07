{
  pkgs, 
  ...
}: {
  # The Nix packages to make available in your workspace
  # Search for packages on https://search.nixos.org/packages
  packages = [ 
    (pkgs.python3.withPackages (ps: [
      ps.flask
      ps.numpy
      ps.midiutil
      ps.librosa
      ps.soundfile
      ps.gtts
      ps.pydub
    ]))
    pkgs.ffmpeg
    pkgs.fluidsynth
    pkgs.git
  ];

  # The VS Code extensions to install in your workspace
  # Find extensions on https://open-vsx.org/
  idx = {
    extensions = [
      "ms-python.python"
    ];

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      # Dependencies are managed by Nix, so pip install is not needed.
      onCreate = {};
      # Runs every time the workspace is (re)started
      onStart = {
        # run-app = "python app.py";
      };
    };

    # Web-based previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["python" "app.py" "--port" "$PORT"];
          manager = "web";
        };
      };
    };
  };
}