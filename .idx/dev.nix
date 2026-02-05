{ pkgs, ... }: {
  # The Nix packages to make available in your workspace
  packages = [
    (pkgs.python3.withPackages (ps: [
      ps.Flask
      ps.numpy
      ps.midiutil
      ps.librosa
      ps.soundfile
    ]))
    pkgs.fluidsynth
    pkgs.ffmpeg
    pkgs.soundfont-fluid
    pkgs.git
  ];

  # Set environment variables for UTF-8 support
  env = {
    LANG = "en_US.UTF-8";
    LC_ALL = "en_US.UTF-8";
  };

  # The VS Code extensions to install in your workspace
  idx = {
    extensions = [
      "ms-python.python"
    ];

    workspace = {
      # The commands to run when the workspace is (re)started
      onStart = {
        # Nix automatically handles the environment setup
      };
    };

    # Web previews
    previews = {
      enable = true;
      previews = {
        web = {
          # The command to start your web server
          command = ["python" "-u" "app.py"];
          manager = "web";
        };
      };
    };
  };
}
