{
  description = "sadbot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        sadbot = pkgs.python3.withPackages(p: with p; [
          pkgs.ffmpeg
          requests
          pillow
          matplotlib
          numpy
          sympy
          html2text
          types-requests
          mypy
          black
          pylint
          yt-dlp
        ]);
        packageName = "sadbot";
      in {
        packages.${packageName} = sadbot;

        defaultPackage = self.packages.${system}.${packageName};

        devShell = sadbot.env;
      });
}
