{
  description = "Pure Python 3.14 Flask Dev Environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      utils,
    }:
    utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Define the python environment with your specific packages
        pythonEnv = pkgs.python314.withPackages (
          ps: with ps; [
            flask
            mariadb
            flask-migrate
            flask-cors
            python-dotenv
            black
            ruff
          ]
        );
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.prettier
          ];
        };
      }
    );
}
