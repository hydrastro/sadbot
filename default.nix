{ pkgs ? import <nixpkgs> {} }:

pkgs.python3Packages.buildPythonApplication {
  pname = "sadbot";
  src = ./.;
  version = "0.1";
  propagatedBuildInputs = [ pkgs.python3Packages.requests pkgs.python3Packages.pillow pkgs.python3Packages.html2text ];
}

