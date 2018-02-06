import argparse
import logging
import os
from timeit import default_timer as timer

import matplotlib
matplotlib.use('Agg') # Fixes weird segfaults, see http://matplotlib.org/faq/howto_faq.html#matplotlib-in-a-web-application-server

from dynamic_pytables_where_condition import read_from_table
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import tables as tb
import yaml


__version__ = '1.0.1'


DEFAULT_CMAP = 'inferno'
FIGURE_SIZE = (11.7, 8.3) # In inches


def plot_modal_composite(base_key, modal_composites, column_units, column_descriptions):
    logging.info("Plotting the '%s' modal composite and its subkeys...", base_key)
    start = timer()

    def _get_column_title(column_name):
        description = column_descriptions[column_name]
        unit = column_units[column_name]
        return description if not unit else "%s [%s]" % (description, unit)

    plt.suptitle(_get_column_title(base_key))

    x = modal_composites['a']
    y = modal_composites['t_b']

    shape = np.unique(x).shape[0], np.unique(y).shape[0]
    X = x.reshape(shape)
    Y = y.reshape(shape)

    if base_key == 'm_dominant':
        subplots_spec = [
            # key_suffix, key_description
            ('',         'direct method'),
            ('',         'direct method (3D overview)'),
        ]
    else:
        subplots_spec = [
            # key_suffix, key_description
            ('',         'direct method'),
            ('',         'direct method (3D overview)'),
            ('_approx',  'approximation via physical dualism'),
            ('_rel_err', 'relative approximation error'),
        ]

    for ax_idx, (key_suffix, key_description) in enumerate(subplots_spec, start=1):
        key = base_key + key_suffix

        z = modal_composites[key]
        Z = z.reshape(shape)

        if '3D' in key_description:
            ax = plt.subplot(2, 2, ax_idx, projection='3d', elev=30.)
            ax.plot_wireframe(X, Y, Z, rcount=0, ccount=10)

            if base_key == 'm_dominant':
                # Rotate the 3D plot to make the dominant modes more visible
                ax.view_init(azim=105)
        else:
            plt.subplot(2, 2, ax_idx)
            plt.imshow(
                Z.T,
                aspect='auto',
                interpolation='none',
                origin='lower',
                extent=[x.min(), x.max(), y.min(), y.max()],
            )
            plt.colorbar()

        plt.title(key_description)
        plt.xlabel(_get_column_title('a'))
        plt.ylabel(_get_column_title('t_b'))

    logging.info("Plotting completed in %f second(s)", timer() - start)

def load_modal_composites(results_file, **filters):
    logging.info("Loading modal composites from '%s'...", results_file)
    start = timer()
    with tb.open_file(results_file) as fp:
        table = fp.root.parameter_sweep.modal_composites
        modal_composites = read_from_table(table, **filters)

        column_units = yaml.load(table.attrs.column_units_as_yaml)
        column_descriptions = yaml.load(table.attrs.column_descriptions_as_yaml)

        logging.info("Loading completed in %f second(s)", timer() - start)
        return modal_composites, column_units, column_descriptions

def configure_matplotlib(cmap=DEFAULT_CMAP):
    matplotlib.rc('figure',
        figsize=FIGURE_SIZE,
        titlesize='xx-large'
    )

    matplotlib.rc('figure.subplot',
        left   = 0.05, # the left side of the subplots of the figure
        right  = 0.99, # the right side of the subplots of the figure
        bottom = 0.06, # the bottom of the subplots of the figure
        top    = 0.91, # the top of the subplots of the figure
        wspace = 0.13, # the amount of width reserved for blank space between subplots
        hspace = 0.25, # the amount of height reserved for white space between subplots
    )

    matplotlib.rc('image',
        cmap=cmap
    )

def analyze_model(model_file, report_file, **filters):
    with PdfPages(report_file) as pdf:
        modal_composites, column_units, column_descriptions = load_modal_composites(model_file, **filters)
        for base_key in ('m_dominant', 'omega', 'sigma_cr'):
            plot_modal_composite(base_key, modal_composites, column_units, column_descriptions)

            pdf.savefig()
            plt.close() # Prevents memory leaks

def main():
    # Setup command line option parser
    parser = argparse.ArgumentParser(
        description='Visualization and modal analysis of the parametric model '\
                    'of buckling and free vibration in prismatic shell '\
                    'structures, as computed by the fsm_eigenvalue project.',
    )
    parser.add_argument(
        'model_file',
        help="File storing the computed parametric model"
    )
    parser.add_argument(
        '-r',
        '--report_file',
        metavar='FILENAME',
        help="Store the modal analysis report to the selected FILENAME, uses '<model_file>.pdf' by default"
    )
    parser.add_argument(
        '--a-min',
        metavar='VAL',
        type=float,
        help='If specified, clip the minimum strip length [mm] to VAL'
    )
    parser.add_argument(
        '--a-max',
        metavar='VAL',
        type=float,
        help='If specified, clip the maximum strip length [mm] to VAL'
    )
    parser.add_argument(
        '--t_b-min',
        metavar='VAL',
        type=float,
        help='If specified, clip the minimum base strip thickness [mm] to VAL'
    )
    parser.add_argument(
        '--t_b-max',
        metavar='VAL',
        type=float,
        help='If specified, clip the maximum base strip thickness [mm] to VAL'
    )
    parser.add_argument(
        '-c',
        '--cmap',
        metavar='CMAP',
        default=DEFAULT_CMAP,
        help="Plot figures using the selected Matplotlib CMAP, '%s' by default" % DEFAULT_CMAP
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        const=logging.WARN,
        dest='verbosity',
        help='Be quiet, show only warnings and errors'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        const=logging.DEBUG,
        dest='verbosity',
        help='Be very verbose, show debug information'
    )
    parser.add_argument(
        '--version',
        action='version',
        version="%(prog)s " + __version__
    )
    args = parser.parse_args()

    # Configure logging
    log_level = args.verbosity or logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(message)s")

    configure_matplotlib(cmap=args.cmap)

    if not args.report_file:
        args.report_file = os.path.splitext(args.model_file)[0] + '.pdf'

    analyze_model(
        model_file=args.model_file,
        report_file=args.report_file,
        a_min=args.a_min,
        a_max=args.a_max,
        t_b_min=args.t_b_min,
        t_b_max=args.t_b_max,
    )

if __name__ == '__main__':
    main()
