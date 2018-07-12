# -*- coding: utf-8 -*-
"""
Created on Thu May 31 20:50:39 2018

@author: jpelda
"""
import os
import sys
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib.colors import from_levels_and_colors
from matplotlib.ticker import FormatStrFormatter
import numpy as np
sys.path.append(os.getcwd() + os.sep + 'memphis' + os.sep + 'utils')
from plotter import plot_format
from matplotlib.patches import Rectangle

class Graphen:

    def __init__(self):
        pass

    def plot_map(self, gdf_census, gdf_paths, gdf_sewnet, gdf_gis_b,
                 gdf_gis_r, wwtp_x=None, wwtp_y=None,
                 paths_lw=1, sewnet_lw=0.65):
        """

        Parameters
        ----------
        gdf_census
        gdf_paths
        gdf_sewnet
        gdf_gis_b
        gdf_gis_r
        wwtp_x
        wwtp_y
        paths_lw
        sewnet_lw

        Returns
        -------

        """
        plot_format()
        fig, ax = plt.subplots(figsize=(16 / 2.54, 9 / 2.54))
        # color_map()
        # cmap_nodes = plt.get_cmap('WhiteRed')
        # vmin_nodes = min(gdf_nodes['wc'])
        # vmax_nodes = 100

        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        levels = [-1, 0, 25, 50, 75, 100, 150, max(gdf_census['inhabs'])]
        colors = ['white', '#C0C9E4', '#9EADD8', '#6D89CB',
                  '#406DBB', '#3960A7', '#2F528F']
        cmap_census, norm_census = from_levels_and_colors(levels, colors)

        gdf_paths_levels = [min(gdf_paths['V']), max(gdf_paths['V'])]
        gdf_paths_colors = ['r']
        # cmap_paths, norm_paths = from_levels_and_colors(gdf_paths_levels,
        #                                                gdf_paths_colors)

        gdf_sewnet_levels = [min(gdf_sewnet['DN']), max(gdf_sewnet['DN'])]
        gdf_sewnet_colors = ['green']
        # cmap_sewnet, norm_sewnet = from_levels_and_colors(gdf_sewnet_levels,
        #                                                  gdf_sewnet_colors)

        sm_census = plt.cm.ScalarMappable(cmap=cmap_census, norm=norm_census)
        sm_census._A = []
        colorBar_census = fig.colorbar(sm_census, ax=ax)

        gdf_census.set_geometry = gdf_census['SHAPE_b']
        gdf_census.plot(ax=ax, cmap=cmap_census, norm=norm_census,
                        column='inhabs', alpha=0.4)

        colorBar_census.ax.set_ylabel("\\small{Inhabitants} "
                                      "$[\\unitfrac{Persons}{10,000  m^2}]$",
                                      fontsize=10,
                                      )

        gdf_gis_b_color = 'black'
        gdf_gis_b_alpha = 0.2
        gdf_gis_b.plot(ax=ax, color=gdf_gis_b_color, alpha=gdf_gis_b_alpha)

        wwtp_legend = []
        if wwtp_x and wwtp_y is not None:
            ax.plot(wwtp_x, wwtp_y, color='black', markersize=10, marker='*')
            wwtp_legend = mlines.Line2D([], [], color='black', marker='*',
                                        linestyle='None', markersize=10,
                                        label='Waste water treatment plant')
        gdf_gis_r_color = 'black'
        gdf_gis_r_alpha = 0.3
        gdf_gis_r_linewidth = 0.3
        gdf_gis_r.plot(ax=ax, color=gdf_gis_r_color,
                       linewidth=gdf_gis_r_linewidth, alpha=gdf_gis_r_alpha)

        gdf_paths.plot(ax=ax, color='r', linewidth=paths_lw)
        gdf_sewnet.plot(ax=ax, color='green', linewidth=sewnet_lw)

        # gdf_paths[gdf_paths.DN >= 800].plot(ax=ax, cmap=cmap_paths,
        # norm=norm_paths,
        #         column="DN", linewidth=1, )
        # gdf_sewnet[gdf_sewnet.width >= 800].plot(ax=ax, cmap=cmap_sewnet,
        #          norm=norm_sewnet, column="width", linewidth=0.8)
        # for x, y, txt in zip(gdf_nodes['x'], gdf_nodes['y'],
        # gdf_nodes.index):
        #    ax.annotate(txt, (x, y))
        # gdf_dhs.plot(ax=ax)

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        gdf_gis_b_legend = mlines.Line2D(
                [], [], color=gdf_gis_b_color, marker='h', linestyle='None',
                markersize=10, label="Buildings", alpha=gdf_gis_b_alpha)
        gdf_gis_r_legend = mlines.Line2D(
                [], [], color=gdf_gis_r_color, linestyle='-',
                linewidth=gdf_gis_r_linewidth, label="Roads",
                alpha=gdf_gis_r_alpha)

        gdf_sewnet_legend = []
        gdf_sewnet_legend.append(
                mlines.Line2D(
                        [], [], color=gdf_sewnet_colors[0],
                        linestyle='-',
                        label="Sewage network {:1.2f} "
                        " m "
                        " $ \\leq $ DN $ \\leq $  {:10.2f}"
                        " m"
                        "".format(
                                  gdf_sewnet_levels[0],
                                  gdf_sewnet_levels[1])))
        # gdf_sewnet_legend.append(mlines.Line2D([], [],
        #                          color=gdf_sewnet_colors[1],
        #                          linestyle='-', label=
        #                         "Sewage network DN {} $\leq$ x $\leq$ DN {} "
        #                          "".format(
        #                          gdf_sewnet_levels[1],
        #                          gdf_sewnet_levels[2])))

        legend_empty = [mlines.Line2D([], [], color='None', linestyle='')]
        # ,                mlines.Line2D([], [], color='None', linestyle='')]
        gdf_path_legend = []
        gdf_path_legend.append(
                mlines.Line2D(
                        [], [], color=gdf_paths_colors[0],
                        linestyle='-',
                        label="Generic sewage network {:1.2f} "
                        " $\\unitfrac{{m^3}}{{s}} \\leq \\dot{{V}} \\leq$ "
                        " {:10.2f} $\\unitfrac{{m^3}}{{s}}$".format(
                                                     gdf_paths_levels[0],
                                                     gdf_paths_levels[1])))
        # gdf_path_legend.append(mlines.Line2D([], [], color=gdf_paths_colors[1],
        #                                linestyle='-',
        #                                label=
        #                                "Generic sewage network DN {} $\leq$ x $\leq$"
        #                                " DN {}".format(
        #                                        gdf_paths_levels[1],
        #                                        gdf_paths_levels[2])))
        # gdf_path_legend.append(mlines.Line2D([], [], color=gdf_paths_colors[2],
        #                                linestyle='-',
        #                                label=
        #                                "Generic sewage network {} $\leq$ {:.0f}"
        #                                " $[DN]$".format(
        #                                        gdf_paths_levels[2],
        #                                        gdf_paths_levels[3])))
        if wwtp_legend == []:
            handles = [gdf_gis_b_legend] + [gdf_gis_r_legend] +\
                   gdf_sewnet_legend + gdf_path_legend
        else:
            handles = [wwtp_legend] + [gdf_gis_b_legend] +\
                        [gdf_gis_r_legend] + gdf_sewnet_legend +\
                        gdf_path_legend

        # Shrink current axis's height by 10% on the bottom
#        box = ax.get_position()
        # ax.set_position([box.x0, box.y0 + box.height * 0.1,
        #                 box.width, box.height * 0.9])

        # ax.legend(handles=handles, loc='lower left',
        # bbox_to_anchor=(0, -0.2),
        #  ncol=3)

        leg = plt.legend(handles=handles, bbox_to_anchor=(0.5, -0.13),
                         borderaxespad=0.12, ncol=2, loc=9)
        leg.get_frame().set_edgecolor('black')
        leg.get_frame().set_linewidth(0.5)

        fig.tight_layout()

        return fig


    def plot_distr_of_nodes(self, dis_sew_in_inh, dis_pat_in_inh,
                            dis_cen_in_inh):
        """

        Parameters
        ----------
        dis_sew_in_inh
        dis_pat_in_inh
        dis_cen_in_inh

        Returns
        -------
        matplotlib.figure()

        """

        sew_y = [dis_sew_in_inh[key] for key in sorted(dis_sew_in_inh.keys())]
        pat_y = [dis_pat_in_inh[key] for key in sorted(dis_pat_in_inh.keys())]
        dev_pat_to_sew = (np.array(sew_y) - np.array(pat_y)) / np.array(sew_y)
        dev_pat_to_sew[dev_pat_to_sew == np.inf] = np.nan
        dev_pat_to_sew[dev_pat_to_sew == -np.inf] = np.nan
        dev_pat_to_sew = dev_pat_to_sew / np.nanmax(abs(dev_pat_to_sew))
        dev_pat_to_sew = 1 - abs(dev_pat_to_sew)

        plot_format()
        fig, ax0 = plt.subplots(figsize=(8 / 2.54, 4.5 / 2.54))
        fig.tight_layout()
        ax1 = ax0.twinx()

        ax0.set_xlabel("Population density "
                       "$[\\unitfrac{Inhabitants}{10,000 m^2}]$")
        ax0.set_ylabel('Match $[-]$')
        ax1.set_ylabel('Frequency $[-]$')

        width = 1

        print("Amount of sewages' points for inhabs = -1: {}".format(
                dis_sew_in_inh[-1]))
        print("Amount of generic sewages' points for inhabs = -1: {}".format(
                dis_pat_in_inh[-1]))
        print("Amount of sewages' points for inhabs = -1: {}".format(
                dis_cen_in_inh[-1]))

        ax0.bar(sorted(dis_sew_in_inh.keys()), dev_pat_to_sew, width=width,
                color='#4472C4',
                label="Match of the points between the networks $[-]$")

#        print("Amount of paths' points for inhabs = -1: {}".format(
#                dis_pat_in_inh[-1]))
#        ax0.bar(np.array(sorted(dis_pat_in_inh.keys())) + width+0.2, pat_y,
#                color='r', width=width, label='Generic sewage network')

        handles0, labels0 = ax0.get_legend_handles_labels()

        y = [dis_cen_in_inh[key] if dis_cen_in_inh[key] != 0 else None for
             key in sorted(dis_cen_in_inh.keys())]

        ax1.plot(sorted(dis_cen_in_inh.keys()), y, color='black', linestyle='',
                 marker='.', markersize=1,
                 label='Frequency of the raster $[-]$')
        handles1, labels1 = ax1.get_legend_handles_labels()

        handles = handles0 + handles1
        labels = labels0 + labels1

        ax0.legend(handles, labels, loc='center', bbox_to_anchor=(0.5, 1.2))

#        _, y1 = ax0.transData.transform((0, 0))
#        _, y2 = ax1.transData.transform((0, 0))
#        inv = ax1.transData.inverted()
#        _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
#        miny, maxy = ax1.get_ylim()
#        ax1.set_ylim(miny+dy, maxy+dy)
        start, end = ax0.get_ylim()
        ax0.set_yticks(np.arange(np.floor(start), 1.1, 0.25))
        ax0.axhline(0, linewidth=0.5, color='black', zorder=3)
#        ax0.set_yscale('symlog')
#        ax0.set_ylim(ymin=-1)
        ax1.set_yscale('symlog')

        ax1.set_ylim(ymin=0)
        
        return fig


    def plot_boxplot(self, data, x_label='', x_rotation=0,
                     y_label='', y_scale='linear', legend_name=None):
        """
        Distribution of generic calculated volumetric flow over real
        network volumetric flow.
        Parameters
        ----------
        data : dict
            dict.keys() give the x names, dict.values() is distribution
        x_label
        x_rotation
        y_label
        y_scale
        legend_name

        Returns
        -------
            matplotlib.figure()
        """

        plot_format()
        fig, ax = plt.subplots(figsize=(8 / 2.54, 4.5 / 2.54))
        fig.tight_layout()

        ax.set_yscale(y_scale)
        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)

        ax.boxplot(data.values())
        x_keys = list(data.keys())
        if -1 in x_keys:
            x_keys[0] = ''

        ax.set_xticklabels(x_keys, rotation=x_rotation)
#        ax.set_xticklabels(data.keys(), rotation=x_rotation)
        if legend_name is not None:
            p_1 = Rectangle((0, 0), 1, 1, fill=False, edgecolor='black')
            ax.legend([p_1], ["Generic network"])

        return fig

    def plot_boxplot_2_beside_in_1(self, data_1, data_2):
        """

        Parameters
        ----------
        data_1
        data_2

        Returns
        -------

        """
        x = np.array(list(data_1.keys()))
        space = (x[::-1][0] - x[::-1][1]) / 5
        plot_format()
        fig, ax = plt.subplots()
        fig.tight_layout(pad=0, w_pad=0, h_pad=0)


        ax.boxplot(data_1.values(), 0, '',
                   positions=np.array(range(len(x))) - 0.1, widths=space)
        ax.boxplot(data_2.values(), 0, '',
                   positions=np.array(range(len(x))) + 0.1, widths=space)

        ax.set_xlim((0 - x[::-1][0] - x[::-1][1], len(x) + 2 * space))
        ax.xaxis.set_ticklabels(x)

        return fig

    def plot_boxplot_2_in_1(self, data_1, data_2, x_label='',
                            x_rotation=0, y_label='', y_scale='linear'):
        """

        Parameters
        ----------
        data_1
        data_2
        x_label
        x_rotation
        y_label
        y_scale

        Returns
        -------

        """
        plot_format()
        fig, ax = plt.subplots(figsize=(8 / 2.54, 4.5 / 2.54))
        fig.tight_layout()

        color = '#4472C4'
        ax.boxplot(data_1.values(), widths=0.4,
                   boxprops=dict(facecolor=color, color=color),
                   capprops=dict(color=color),
                   whiskerprops=dict(color=color),
                   flierprops=dict(color=color, markeredgecolor=color),
                   medianprops=dict(color='black'),
                   patch_artist=True)
        ax.boxplot(data_2.values(), widths=0.8)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_yscale(y_scale)

        x_keys = sorted(list(data_1.keys()))
        if -1 in x_keys:
            x_keys[0] = ''
        ax.set_xticklabels(x_keys, rotation=x_rotation)

        p_1 = Rectangle((0, 0), 1, 1, fc=color)
        p_2 = Rectangle((0, 0), 1, 1, fill=False, edgecolor='black')
        ax.legend([p_1, p_2], ["Generic network", "Sewage network"],
                  ncol=2)

        return fig


if __name__ == '__main__':
    import Visualisation

    vis = Graphen()
    vis.plot_boxplot({'helo': [12, 32, 43]}, 'test', 'test')

else:
    pass
