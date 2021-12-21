from .helper import Helper


class Halfedge:
    @staticmethod
    def get_verts(halfedge, commands) -> list:
        """ Input commands (series of halfedge operation) to get multiple verts
        """
        vert_list = []
        for c in commands:
            if c == 1:    # Next halfedge
                halfedge = halfedge.link_loop_next
            elif c == 2:  # Previous halfedge
                halfedge = halfedge.link_loop_prev
            elif c == 3:  # Opposite halfedge
                halfedge = halfedge.link_loop_radial_next
            else:         # Get vert (c==4)
                vert_list.append(halfedge.vert)
        return halfedge, vert_list

    @staticmethod
    def get_single_vert(halfedge, commands):
        """ Input commands (series of halfedge operation) then get a single vert
        """
        halfedge, vert_list = Halfedge.get_verts(halfedge, commands)
        return vert_list[0]

    @staticmethod
    def get_verts_repeat_n_times(halfedge, commands, repeat_times, get_vert_order, num_verts_reserved) -> list:
        """ Repeat commands for n times and also get verts
        """
        unordered_verts = []
        for i in range(repeat_times):
            halfedge, vert_list = Halfedge.get_verts(halfedge, commands)
            unordered_verts.extend(vert_list)

        return Helper.reorder_list(unordered_verts, get_vert_order, num_verts_reserved)
