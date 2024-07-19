import click
from serial_toolbox.ui import serial_monitor

@click.group()
def main():
    """
    Serial Toolbox CLI

    Examples
    --------
    To run the serial monitor:
    $ sertools monitor -c path/to/config.yaml
    """
    pass

@main.command()
@click.option('-c', '--config', type=click.Path(exists=True), required=True, help='Path to the configuration file.')
def monitor(config):
    """
    Start the Serial Monitor CLI with configuration from CONFIG_FILE.

    Parameters
    ----------
    config : str
        Path to the configuration file.
    """
    serial_monitor(config)

if __name__ == "__main__":
    main()