{
  description = "Python development environment using uv and nix-managed packages";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
      pythonPkg = pkgs.python3;
      pythonEnv = pythonPkg.withPackages (p: [
        # Libraries that can't be managed by uv due to dynamic linking issues
        # or those you want nix to manage explicitly
      ]);
    in {
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          uv
          pythonPkg
          pythonEnv
          pyright
          ruff
        ];

        shellHook = ''
          export UV_PYTHON_PREFERENCE="only-system"
          export UV_PYTHON="${pythonPkg}"
        '';
      };
    });
}
