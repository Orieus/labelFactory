# -*- coding: utf-8 -*-
import sys
if sys.version_info.major == 3:
    import tkinter as tk
else:
    import Tkinter as tk


class LabelViewGeneric(tk.Frame):
    """Encapsulates of all the GUI logic.

    Represents a window with labels and buttons

    Attributes:
        master: where to open the Frame, by deafult root window
        main_label: Main Label indicating the task.
        url_label : Url Label we are considering now.
        yes       : Button to indicate that the answer to main_label is "yes"
                    for url_label
        no        : Button to indicate that the answer to main_label is "no"
                    for url_label
        error     : Button to indicate that webpage for url_label is not
                    correct
    """

    def __init__(self, categories, master=None, cat_model='single',
                 parent_cat={}):

        tk.Frame.__init__(self, master)
        master.wm_attributes("-topmost", 1)
        self.grid()

        # Initializations
        self.mybuttons = None
        self.url_label = None
        self.main_label = None
        self.cat_model = cat_model
        self.parent_cat = parent_cat

        self.createWidgets(categories)

    def update_guilabel(self, new_label):
        """ Updates the Url label to show.

           If url is None then the window is destroyed. Nothing left to label

           Args:
                new_label: url to put as label in the window.
                If None the GUI is destroyed
        """

        if self.cat_model == 'single':
            self.url_label.configure(text=new_label)
        else:
            self.url_label['state'] = 'normal'
            self.url_label.delete(1.0, tk.END)
            self.url_label.insert(tk.END, new_label)
            self.url_label['state'] = 'disabled'
        self.master.update()

        # This is the old version. Not needed because new_label is not None
        # if new_label:
        #     self.url_label.configure(text=new_label)
        #     self.master.update()
        # else:
        #     self.master.destroy()

    def start_gui(self, new_label):
        """ Starts the GUI, puting the initial Url to show.

           If url is None then the window is destroyed. Nothing left to label

           Args:
                new_label: url to put as label in the window.
                If None the GUI is not started
        """

        if new_label:
            if self.cat_model == 'single':
                self.url_label.configure(text=new_label)
            else:
                self.url_label['state'] = 'normal'
                self.url_label.delete(1.0, tk.END)
                self.url_label.insert(tk.END, new_label)
                self.url_label['state'] = 'disabled'
                # textoprueba = (
                #     "ANALISIS DE LA INTERACCION DE LA REPLICASA DEL VIRUS DE" +
                #     " LA HEPATITIS C CON LA QUINASA CELULAR AKT/PKB \n" +
                #     "LOS VIRUS SON PARASITOS INTRACELULARES OBLIGADOS QUE " +
                #     "INTERACCIONAN CON LA MAQUINARIA CELULAR EN TODOS Y CADA UNO DE LOS PASOS DE SU CICLO REPLICATIVO.  EL CONOCIMIENTO DE LA INTERACCION VIRUS-CELULA ABRE OPORTUNIDADES PARA MODULAR CADA UNO DE LOS COMPONENTES DE DICHA INTERACCION, ASI COMO LA INTERACCION MISMA. EL VIRUS DE LA HEPATITIS C (HCV) ES UN VIRUS CON TROPISMO HEPATICO, AGENTE CAUSAL DE LA HEPATITIS C, Y PRINCIPAL CAUSANTE DE CIRROSIS Y CARCINOMA HEPATOCELULAR. LAS RELACIONES QUE EL HCV ESTABLECE CON COMPONENTES CELULARES INCLUYEN, ENTRE OTROS, RECEPTORES DE MEMBRANA, PROTEINAS IMPLICADAS EN RUTAS DE SEÑALIZACION Y CONTROL DE CICLO CELULAR, RUTAS DEL METABOLISMO DEL RNA, ETC. MI GRUPO TIENE UNA GRAN EXPERIENCIA PREVIA EN EL ESTUDIO Y ANALISIS DE LA POLIMERASA DEL HCV. DESDE HACE UNOS AÑOS, Y COMO CONSECUENCIA DE UNA ESTANCIA POSDOCTORAL PREVIA DEL INVESTIGADOR PRINCIPAL, LA LINEA DE INVESTIGACION SE HA ABIERTO A FACTORES CELULARES QUE INTERACCIONAN CON LA POLIMERASA VIRAL. FRUTO DE ESTE TRABAJO, MI GRUPO DEFINIO LA INTERACCION DE NS5B CON EL RECEPTOR ALFA DE ESTROGENOS. MUY RECIENTEMENTE, Y LIDERANDO LA COLABORACION CON OTROS GRUPOS, HEMOS DEFINIDO LA INTERACCION DE NS5B CON LA QUINASA CELULAR AKT/PKB. LOS RESULTADOS OBTENIDOS, ACTUALMENTE ENVIADOS PARA SU PUBLICACION, INCLUYEN LA FOSFORILACION IN VITRO DE NS5B POR AKT/PKB RECOMBINANTE, EL EFECTO QUE UN INHIBIDOR ESPECIFICO DE AK/PKB PROVOCA EN EL MANTENIMIENTO DE UN REPLICON SUBGENOMICO O EN CELULAS INFECTADAS CON HCVCC, ASI COMO LA INTERACCION PROPIAMENTE DICHA ANALIZADA MEDIANTE EXPERIMENTOS DE CO-INMUNOPRECIPITACION. ADEMAS, LA CO-LOCALIZACION INTRACELULAR DE AKT/PKB CON NS5B, BIEN EXPRESADAS ECTOPICAMENTE DE MANERA TRANSITORIA (TRANSFECCION DE PLASMIDOS) O DE MANERA ESTABLE (MANTENIENDO UN REPLICON SUBGENOMICO), BIEN EN CELULAS QUE SOPORTAN ACTIVAMENTE LA INFECCION CON HCVCC, NOS HA PERMITIDO CONCLUIR QUE LA INTERACCION NS5B-AKT/PKB INDUCE UN CAMBIO EN LA LOCALIZACION INTRACELULAR DE AKT/PKB, PASANDO DE CITOPLASMICA A PERINUCLEAR, DONDE SE SITUAN LOS COMPLEJOS REPLICATIVOS DE HCV. OTROS GRUPOS HAN DEMOSTRADO QUE LA ACTIVACION DE AKT/PKB ES CRUCIAL EN LOS PASOS INICIALES DE LA INFECCION POR HCV, PERMITIENDO LA ENTRADA DEL VIRUS EN LA CELULA (LIU ET AL, J BIOL CHEM. 2012;287:41922-30; HUANG ET AL AUTOPHAGY. 2013;9(2):175-95). ESTA ACTIVACION, QUE TIENE LUGAR EN LA MEMBRANA PLASMATICA, DESAPARECE A LAS POCAS HORAS POSTINFECCION. ESTOS RESULTADOS PREVIOS TANTO DEL NUESTRO COMO DE OTROS GRUPOS NOS ANIMAN A SOLICITAR UN PROYECTO QUE NOS PERMITA AHONDAR EN ESTA INTERACCION, DEFINIENDO I) LOS RESIDUOS DE NS5B IMPLICADOS EN LA INTERACCION CON AKT/PKB, II) LOS RESIDUOS DE NS5B QUE SON FOSFORILADOS POR AKT/PKB, III) EL EFECTO QUE DICHA FOSFORILACION TENDRIA EN LA ACTIVIDAD DE NS5B, IV) EL EFECTO QUE EL CAMBIO DE LOCALIZACION DE AKT/PKB TIENE SOBRE EL CICLO REPLICATIVO DE HCV (PROBAR EL PRINCIPIO DE EXCLUSION DE LA SUPERINFECCION), Y V) EL EFECTO QUE NS5B TIENE SOBRE LA VIA DE SEÑALIZACION PI3K-AKT/PKB-MTOR. EL OBJETIVO ULTIMO DEL PRESENTE PROYECTO SERIA UN CONOCIMIENTO EXHAUSTIVO DE LA INTERACCION NS5B-AKT/PKB QUE PERMITA A MEDIO PLAZO LA POSIBLE MODULACION DE LAS ACTIVIDADES DE NS5B (EFECTO ANTIVIRAL) Y/O DE AKT/PKB (EFECTO ANTICANCERIGENO).")
                # self.url_label.insert(tk.END, textoprueba)

            self.mainloop()
        else:
            self.master.destroy()

    def createWidgets(self, categories):

        """ Create the labeling window with one button per category.
        """

        # The configurations is arbitrary:
        n_cat = len(categories)

        if n_cat < 10:

            # Maybe I should set this as a configurable parameter.
            n_cols = 3

            # Create the main label
            self.main_label = tk.Label(
                self, text=" Select the correct labels ")
            self.main_label.grid(
                row=0, column=0, columnspan=n_cols, sticky=tk.E+tk.W)

            # Create the url label but without the text yet.
            r = 1
            if self.cat_model == 'single':
                self.url_label = tk.Label(self)
                self.url_label.grid(
                    row=r, column=0, columnspan=n_cols, sticky=tk.E+tk.W)
                r += 1

            # Create the collection of buttons
            c = 0
            self.mybuttons = {}
            for class_name in categories:

                # This is just an assignment of a button at object 'self', at
                # the attribute with the name contained in class_name.
                self.mybuttons[class_name] = tk.Button(
                    self, text=class_name, bg='magenta',
                    activebackground='red', activeforeground='green',
                    disabledforeground='cyan')
                self.mybuttons[class_name].grid(row=r, column=c)
                c = (c + 1) % 3
                r = r + (c == 0)

            # Error button
            self.mybuttons['error'] = tk.Button(self)
            self.mybuttons['error']["text"] = "Error"
            self.mybuttons['error'].grid(row=r, column=c)

            if self.cat_model == 'multi':

                # Add one more buttom to finish labeling
                c = (c + 1) % 3
                r = r + (c == 0)
                self.mybuttons['end'] = tk.Button(self, text="END")
                self.mybuttons['end'].grid(row=r, column=c, sticky=tk.W)

                # Create the main label
                self.url_label = tk.Text(
                    self, height=30, width=120, wrap=tk.WORD, relief=tk.SUNKEN,
                    bg='white')
                self.url_label.grid(
                    row=r+1, column=0, rowspan=40, columnspan=120)

        else:

            # Get list of root categories:
            root_cats = [c for c, p in self.parent_cat.items() if p is None]

            # Get subcats for each root category
            subcats = {}
            for rc in root_cats:
                subcats[rc] = [c for c, p in self.parent_cat.items()
                               if p == rc]

            # maxumum number of columns:
            n_cols = max([len(s) for p, s in subcats.items()])

            # Create the main label
            self.main_label = tk.Label(
                self, text=" Select the correct labels ")
            self.main_label.grid(
                row=0, column=0, columnspan=n_cols, sticky=tk.E+tk.W)

            # Create the url label but without the text yet.
            r = 1
            if self.cat_model == 'single':
                self.url_label = tk.Label(self)
                self.url_label.grid(
                    row=r, column=0, columnspan=n_cols, sticky=tk.E+tk.W)
                r += 1

            # Create the collection of buttons
            self.mybuttons = {}
            for rc, sc in subcats.items():

                c = 0
                # Create button for the root class
                self.mybuttons[rc] = tk.Button(self, text=rc)
                self.mybuttons[rc].grid(row=r, column=c, sticky=tk.W)

                for class_name in sc:

                    c += 1
                    # Create button for the subcategories of the root class
                    self.mybuttons[class_name] = tk.Button(
                        self, text=class_name)
                    self.mybuttons[class_name].grid(row=r, column=c,
                                                    sticky=tk.W)

                r += 1

            # Error button
            self.mybuttons['error'] = tk.Button(self, text="Error")
            self.mybuttons['error'].grid(row=r, column=c, sticky=tk.W)

            if self.cat_model == 'multi':

                # Add one more buttom to finish labeling
                c += 1
                self.mybuttons['end'] = tk.Button(self, text="END")
                self.mybuttons['end'].grid(row=r, column=c, sticky=tk.W)

                # Create the main label
                self.url_label = tk.Text(
                    self, height=30, width=120, wrap=tk.WORD, relief=tk.SUNKEN,
                    bg='white')
                self.url_label.grid(
                    row=r+1, column=0, rowspan=40, columnspan=120)
 
