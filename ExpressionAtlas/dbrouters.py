from ExpressionAtlas.models import TissueExpression

class MyDBRouter(object):

    def db_for_read(self, model, **hints):
        """ reading TissueExpression from tissue_expession_data """
        if model == TissueExpression:
            return 'tissue_expession_data'
        return None

    def db_for_write(self, model, **hints):
        """ writing TissueExpression to tissue_expession_data """
        if model == TissueExpression:
            return 'tissue_expession_data'
        return None