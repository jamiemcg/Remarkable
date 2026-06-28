{
  description = "Remarkable — a fully featured Markdown editor for Linux (GTK 3)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      inherit (pkgs) lib;

      # Installable package: `nix run` / `nix build`
      remarkable = pkgs.python3.pkgs.buildPythonApplication {
        pname = "remarkable";
        version = "1.95";
        src = ./.;
        pyproject = true;

        build-system = [ pkgs.python3.pkgs.setuptools ];

        nativeBuildInputs = [
          pkgs.wrapGAppsHook3
          pkgs.gobject-introspection
        ];

        buildInputs = [
          pkgs.gtk3
          pkgs.gtksourceview3
          pkgs.webkitgtk_4_1
          pkgs.pango
        ];

        dependencies = with pkgs.python3.pkgs; [
          pygobject3
          pycairo
          markdown
          beautifulsoup4
          pygtkspellcheck
        ];

        dontWrapGApps = true;
        makeWrapperArgs = [
          "\${gappsWrapperArgs[@]}"
          "--prefix"
          "PATH"
          ":"
          (lib.makeBinPath [ pkgs.wkhtmltopdf ])
        ];

        pythonImportsCheck = [
          "remarkable"
          "remarkable_lib"
          "pdfkit"
        ];
      };

      devPython = pkgs.python3.withPackages (
        ps: with ps; [
          pygobject3
          pycairo
          pygtkspellcheck
        ]
      );
    in
    {
      packages.${system}.default = remarkable;
      apps.${system}.default = {
        type = "app";
        program = "${remarkable}/bin/remarkable";
      };

      # Dev shell: `nix develop` then `uv run remarkable`
      devShells.${system}.default = pkgs.mkShell {
        nativeBuildInputs = [
          pkgs.wrapGAppsHook3
          pkgs.gobject-introspection
        ];

        buildInputs = [
          devPython
          pkgs.uv
          pkgs.gtk3
          pkgs.gtksourceview3
          pkgs.webkitgtk_4_1
          pkgs.pango
          pkgs.wkhtmltopdf
        ];

        shellHook = ''
          export UV_PYTHON_DOWNLOADS=never
          export UV_PYTHON="${devPython}/bin/python"

          if [ ! -e .venv/pyvenv.cfg ]; then
            "${devPython}/bin/python" -m venv --system-site-packages .venv
          fi

          echo "Remarkable dev shell ready. Launch with:  uv run remarkable"
        '';
      };
    };
}
