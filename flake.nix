{
  description = "PSET 4";

  inputs = {
    # Pinned to NixOS 25.11 stable, commit from 2025-12-06
    nixpkgs.url = "github:NixOS/nixpkgs/d9bc5c7dceb30d8d6fafa10aeb6aa8a48c218454";
    flake-utils.url = "github:numtide/flake-utils";
    resources.url = "git+https://codeberg.org/yuuhikaze/resources";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      resources,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells = {
          default = pkgs.mkShell {
            inputsFrom = [
              (resources.outputs.devShells.${system}.docs-converters {
                withPandoc = true;
              })
              resources.outputs.devShells.${system}.docs-templates
            ];
          };
          resources = pkgs.mkShell {
            packages = [ pkgs.miniserve ];
            inputsFrom = [ resources.devShells.${system}.docs-templates ];
          };
        };
      }
    );
}
